import traceback
try:
	from agent.graph.workflow_graph import create_state_graph
	g = create_state_graph()
	print('OK')
except Exception:
	traceback.print_exc()
	raise
