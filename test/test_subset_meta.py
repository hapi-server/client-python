from hapiclient.util import HAPIError, subset_meta

meta = {
"parameters": [
        {"name": "Time"},
        {"name": "Parameter1"},
        {"name": "Parameter2"},
        {"name": "Parameter3"}
    ]
}

msg_o = "Exception not raised by subset_meta() with "

def test_simple():
  params = 'Parameter1,Parameter2'
  subset_meta(meta, params)
  assert len(meta['parameters']) == 3
  assert meta['parameters'][0]['name'] == 'Time'
  assert meta['parameters'][1]['name'] == 'Parameter1'
  assert meta['parameters'][2]['name'] == 'Parameter2'


def test_params_wrong_order():
  params = 'Parameter2,Parameter1'
  try:
    subset_meta(meta, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith('Order of requested parameters does not match')
  else:
    assert False, msg_o + "parameters in wrong order."


def test_params_duplicate_name():
  params = 'Parameter1,Parameter1'
  try:
    subset_meta(meta, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith('Duplicate parameters in requested parameter list')
  else:
    assert False, msg_o + "duplicate parameter names."


def test_params_invalid_name():
  params = 'Parameter1,ParameterX'
  try:
    subset_meta(meta, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith("Parameter 'ParameterX' is not in metadata from server")
  else:
    assert False, msg_o + "invalid parameter name."


def test_params_empty_value():
  params = 'Parameter2,'
  try:
    subset_meta(meta, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith('Empty parameter name')
  else:
    assert False, msg_o + "empty parameter name."


def test_params_leading_space():
  params = ' Parameter1,Parameter2'
  try:
    subset_meta(meta, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith('Leading space')
  else:
    assert False, msg_o + "leading space in parameter name."


def test_params_trailing_space():
  params = 'Parameter1,Parameter2 '
  try:
    subset_meta(meta, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith('Trailing space')
  else:
    assert False, msg_o + "trailing space in parameter name."


def test_params_time_given():
  params = 'Time,Parameter1'
  subset_meta(meta, params)
  assert len(meta['parameters']) == 2
  assert meta['parameters'][0]['name'] == 'Time'
  assert meta['parameters'][1]['name'] == 'Parameter1'


def test_meta_duplicate_names():
  meta_dup = {
    "parameters": [
        {"name": "Time"},
        {"name": "Parameter1"},
        {"name": "Parameter1"},
        {"name": "Parameter3"}
    ]
  }
  params = 'Parameter1'
  try:
    subset_meta(meta_dup, params)
  except Exception as e:
    assert isinstance(e, HAPIError)
    assert str(e).startswith('Duplicate parameter names in metadata returned by server')
  else:
    assert False, msg_o + "duplicate parameter names in metadata returned by server."


if __name__ == "__main__":
  test_simple()
  test_params_wrong_order()
  test_params_duplicate_name()
  test_params_invalid_name()
  test_params_empty_value()
  test_params_leading_space()
  test_params_trailing_space()
  test_params_time_given()
  test_meta_duplicate_names()