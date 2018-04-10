from tests._test_context import ContextTest

def test_state_get(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark(ContextTest.test_state_get, ct)
	return

def test_state_set(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark(ContextTest.test_state_set, ct)
	return

def test_state_delete(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark(ContextTest.test_state_delete, ct)
	return

def test_add_receipt_data(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark(ContextTest.test_add_receipt_data, ct)
	return

def test_add_event(benchmark):
	ct = ContextTest()
	ct.setUp()
	result = benchmark(ContextTest.test_add_event, ct)
	return