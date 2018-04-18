from tests._test_context import ContextTest

def test_state_get(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark.pedantic(ct.test_state_get)
	return

def test_state_set(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark.pedantic(ct.test_state_set)
	return

def test_state_delete(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark.pedantic(ct.test_state_delete)
	return

def test_add_receipt_data(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark.pedantic(ct.test_add_receipt_data)
	return

def test_add_event(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark.pedantic(ct.test_add_event)
	return