from typing import Dict, List

from models import (
    SELF_TEST_INPUT,
    Descriptors600Model,
    Descriptors3000Model,
    DescriptorsWithTaxonomiesModel,
    JustTaxonomiesModel,
    Word2vecModel,
    DescriptorsAllModel,
    Scaler)


# Load the models into memory 

word2vec_model = Word2vecModel()
scaler = Scaler()
MODEL_600 = Descriptors600Model(word2vec_model=word2vec_model, scaler=scaler)
MODEL_3000 = Descriptors3000Model(word2vec_model=word2vec_model, scaler=scaler)
MODEL_ALL = DescriptorsAllModel(word2vec_model=word2vec_model, scaler=scaler)
# MODEL_WITH_TAX = DescriptorsWithTaxonomiesModel(word2vec_model=word2vec_model, scaler=scaler)
# MODEL_JUST_TAX = JustTaxonomiesModel(word2vec_model=word2vec_model, scaler=scaler)

def _predict(text: str) -> Dict[str, List[Dict[str, str]]]:
    global MODEL_600
    global MODEL_3000
    global MODEL_ALL
    # global MODEL_WITH_TAX
    # global MODEL_JUST_TAX
    result_600 = MODEL_600.predict(text)
    result_3000 = MODEL_3000.predict(text)
    result_all = MODEL_ALL.predict(text)
    # result_with_tax = MODEL_WITH_TAX.predict(text)
    # result_just_tax = MODEL_JUST_TAX.predict(text)
    results = {
        'descriptors600': [
            {'label': x.label, 'score': "{0:.5f}".format(x.score)} for x in result_600
        ],
        'descriptors3000': [
            {'label': x.label, 'score': "{0:.5f}".format(x.score)} for x in result_3000
        ],
        'allDescriptors': [
            {'label': x.label, 'score': "{0:.5f}".format(x.score)} for x in result_all
        ],
        # 'descriptorsAndTaxonomies': [
        #     {'label': x.label, 'score': "{0:.5f}".format(x.score)} for x in result_with_tax
        # ],
        # 'taxonomies': [
        #     {'label': x.label, 'score': "{0:.5f}".format(x.score)} for x in result_just_tax
        # ],
    }
    return results

## EXAMPLE INPUT
text = "Federal agents show stronger force at Portland protests despite order to withdraw"

result = _predict(text)
print(result)


