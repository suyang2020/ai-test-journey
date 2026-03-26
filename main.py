from __future__ import annotations

from typing import List, Optional, TypedDict

from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    """LangGraph 状态：messages + test_result。"""

    messages: List[str]
    test_result: Optional[str]


@tool
def write_test(user_input: str) -> str:
    """Generate unit tests for the given input.

    Placeholder only; real logic will be implemented later.
    """

    raise NotImplementedError("write_test 工具逻辑尚未实现")


def generator(state: State) -> State:
    """根据用户输入调用 write_test 工具，并写入 test_result。"""

    messages = state.get("messages", [])
    user_input = messages[-1] if messages else ""

    try:
        tool_result = write_test.invoke({"user_input": user_input})
    except NotImplementedError:
        tool_result = "TODO: write_test 工具逻辑尚未实现"

    # 这里暂时不修改 messages 的结构，只更新 test_result
    return {"messages": messages, "test_result": tool_result}


def build_graph():
    builder = StateGraph(State)
    builder.add_node("generator", generator)
    builder.add_edge(START, "generator")
    builder.add_edge("generator", END)
    return builder.compile()


def main():
    graph = build_graph()

    print("LangGraph 状态图已初始化。输入任意文本后回车，输入 q 退出。")
    while True:
        user_input = input("请输入：").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            break

        state: State = {"messages": [user_input], "test_result": None}
        result = graph.invoke(state)

        print("test_result:", result["test_result"])


if __name__ == "__main__":
    main()
