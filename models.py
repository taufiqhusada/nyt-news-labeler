import abc
import os
import json
import pickle
from typing import List
import logging

import gensim
from keras.models import load_model
from nltk.tokenize import word_tokenize
import numpy as np

logger = logging.getLogger(__name__)

# https://globalvoices.org/2019/10/08/we-too-love-money-more-than-freedom-south-park-creators-mock-nba-with-a-sarcastic-apology-to-china/
SELF_TEST_INPUT = """
South Park creators mock the NBA with a sarcastic apology to China
===
The producers of the American animated sitcom South Park issued a sarcastic apology to China after Beijing censors
deleted every trace of the cartoon on all video streaming services and social media platforms within mainland China.
The apology, published on October 7, mocks the American National Basketball Association (NBA) for bringing “the Chinese
censors into our homes and into our hearts”. The humorous statement follows a global online row caused by a tweet posted
by Daryl Morey, the general manager of Houston Rockets, a team playing in the NBA, in which he supports the Hong Kong
protesters for more political freedom and oppose Beijing policies.
What triggered the Chinese censors’ action is the latest episode of the series, called “Band in China”. It depicts one
of the main characters, Randy, on a business trip in China during which he lands in jail where he meets Disney
characters including Winnie the Pooh and Piglet.
The episode, which mocks Hollywood for its self-censorship practices in China, was released on October 2, just one day
after the 70th anniversary of the foundation of the People's Republic of China.
The episode shocked some of the cartoon's fans both inside and outside China for its violent scenes, which is typical of
the series since its debut in 1997.
"""

DEFAULT_MAX_PREDICTIONS = 5
"""Max. predictions to come up with."""


class MissingModelsException(Exception):
    """Exception that's thrown when the models are missing."""
    pass


def _default_models_dir() -> str:
    """
    Return default path to directory with models.
    :return: Path to directory with models.
    """
    pwd = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(pwd, 'models')
    assert os.path.isdir(models_dir), "Models path should be directory: %s" % models_dir
    return models_dir


class Prediction(object):
    """Single prediction."""

    __slots__ = [
        'label',
        'score',
    ]

    def __init__(self, label: str, score: float):
        self.label = label
        self.score = score


class _BaseLoader(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def _initialize_model(self, models_dir: str) -> None:
        """
        Initialize model and get it ready for prediction.
        :param models_dir: Directory to where models are to be found.
        """
        raise NotImplemented("Abstract method.")

    def __init__(self, models_dir: str = None):
        """
        Initialize model.
        :param models_dir: (optional) Directory to where models are to be found.
        """
        if not models_dir:
            models_dir = _default_models_dir()
        if not os.path.isdir(models_dir):
            raise MissingModelsException("Models directory does not exist at %s" % models_dir)

        logger.debug("    Loading model %s..." % self.__class__.__name__)
        self._initialize_model(models_dir=models_dir)
        logger.debug("    loaded model %s." % self.__class__.__name__)


class _BaseModel(_BaseLoader, metaclass=abc.ABCMeta):
    """Base model class."""

    @abc.abstractmethod
    def predict(self, text: str, max_predictions: int = DEFAULT_MAX_PREDICTIONS) -> List[Prediction]:
        """
        Predict text.
        :param text: Text to run predictions against.
        :param max_predictions: Max. predictions to come up with.
        :return: Predictions.
        """
        raise NotImplemented("Abstract method.")


class Word2vecModel(_BaseModel):
    """Google News word2vec model."""

    __slots__ = [
        '_model',
    ]

    _BASE_NAME = "GoogleNews-vectors-negative300.keyedvectors.bin"

    def _initialize_model(self, models_dir: str) -> None:
        vectors_bin_path = os.path.join(models_dir, self._BASE_NAME)
        vectors_npy_path = os.path.join(models_dir, self._BASE_NAME + '.vectors.npy')

        if not os.path.isfile(vectors_bin_path):
            raise MissingModelsException("Vectors .bin file does not exist at %s" % vectors_bin_path)
        if not os.path.isfile(vectors_npy_path):
            raise MissingModelsException("Vectors .npy file does not exist at %s" % vectors_npy_path)

        self._model = gensim.models.KeyedVectors.load(vectors_bin_path)

    def predict(self, text: str, max_predictions: int = DEFAULT_MAX_PREDICTIONS) -> List[Prediction]:
        raw_predictions = self._model.predict(text)
        predictions = [Prediction(label=x[0], score=x[1]) for x in raw_predictions[:max_predictions]]
        return predictions

    def raw_word2vec_model(self):
        """
        Return raw KeyedVectors model.
        :return: Raw KeyedVectorsModel.
        """
        return self._model


class Scaler(_BaseLoader):
    __slots__ = [
        '_scaler',
    ]

    def _initialize_model(self, models_dir: str) -> None:
        """
        Initialize model and get it ready for prediction.
        :param models_dir: Directory to where models are to be found.
        """
        # Load pre-trained scaler used by all the models
        scaler_path = os.path.join(models_dir, 'scaler')
        if not os.path.isfile(scaler_path):
            raise MissingModelsException("Scaler was not found in %s" % scaler_path)

        with open(os.path.join(models_dir, "scaler"), mode='rb') as scaler_file:
            self._scaler = pickle.load(scaler_file, encoding='latin1')

    def raw_scaler(self):
        return self._scaler


class _TopicDetectionBaseModel(_BaseModel, metaclass=abc.ABCMeta):
    """Base topic detection model."""

    __slots__ = [
        '_raw_word2vec_model',
        '_raw_scaler',
        '_keras_model',
        '_labels',
    ]

    _PUNCTUATION = '.,:;!?()/\"-<>[]{}|\\@#`$%^&*'

    @staticmethod
    @abc.abstractmethod
    def _model_basename() -> str:
        """
        Return file basename (without extension) of model to load
        :return: File basename of model to load, e.g. 'descriptors_600'.
        """
        raise NotImplemented("Abstract method")

    def _initialize_model(self, models_dir: str) -> None:

        assert self._raw_word2vec_model, "Raw word2vec model is unset."
        assert self._raw_scaler, "Scaler is unset."

        model_basename = self._model_basename()
        assert model_basename, "Model basename is empty."

        json_model_path = os.path.join(models_dir, '%s.json' % model_basename)
        hdf5_model_path = os.path.join(models_dir, '%s.hdf5' % model_basename)

        if not os.path.isfile(json_model_path):
            raise MissingModelsException("JSON model was not found in %s" % json_model_path)
        if not os.path.isfile(hdf5_model_path):
            raise MissingModelsException("HDF5 model was not found in %s" % hdf5_model_path)

        with open(json_model_path, 'r') as data_file:
            self._keras_model = load_model(hdf5_model_path)
            self._labels = json.load(data_file)

    def __init__(self, word2vec_model: Word2vecModel, scaler, models_dir: str = None):
        assert word2vec_model, "word2vec model is unset."
        assert scaler, "Scaler is unset."

        self._raw_word2vec_model = word2vec_model.raw_word2vec_model()
        self._raw_scaler = scaler.raw_scaler()

        super().__init__(models_dir=models_dir)

    def predict(self, text: str, max_predictions: int = DEFAULT_MAX_PREDICTIONS) -> List[Prediction]:
        if type(self._keras_model.input) == list:
            _, sample_length, embedding_size = self._keras_model.input_shape[0]
        else:
            _, sample_length, embedding_size = self._keras_model.input_shape

        words = [w.lower() for w in word_tokenize(text)
                 if w not in self._PUNCTUATION][:sample_length]
        x_matrix = np.zeros((1, sample_length, embedding_size))

        for i, w in enumerate(words):
            if w in self._raw_word2vec_model:
                word_vector = self._raw_word2vec_model[w].reshape(1, -1)
                scaled_vector = self._raw_scaler.transform(word_vector, copy=True)[0]
                x_matrix[0][i] = scaled_vector

        if type(self._keras_model.input) == list:
            x = [x_matrix] * len(self._keras_model.input)
        else:
            x = [x_matrix]

        y_predicted = self._keras_model.predict(x)

        zipped = zip(self._labels, y_predicted[0])

        raw_predictions = sorted(zipped, key=lambda elem: elem[1], reverse=True)

        predictions = [
            # Filter out 'count' in all_descriptors.json
            Prediction(label=x[0] if isinstance(x[0], str) else x[0]['word'], score=x[1])
            for x in raw_predictions[:max_predictions]
        ]

        return predictions


class Descriptors600Model(_TopicDetectionBaseModel):

    @staticmethod
    def _model_basename() -> str:
        return 'descriptors_600'


class Descriptors3000Model(_TopicDetectionBaseModel):

    @staticmethod
    def _model_basename() -> str:
        return 'descriptors_3000'


class DescriptorsAllModel(_TopicDetectionBaseModel):

    @staticmethod
    def _model_basename() -> str:
        return 'all_descriptors'


class DescriptorsWithTaxonomiesModel(_TopicDetectionBaseModel):

    @staticmethod
    def _model_basename() -> str:
        return 'descriptors_with_taxonomies'


class JustTaxonomiesModel(_TopicDetectionBaseModel):

    @staticmethod
    def _model_basename() -> str:
        return 'just_taxonomies'
