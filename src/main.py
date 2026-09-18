import os
from calendar_service import CalendarService
from helpers import parse_datetimeinput
from dotenv import load_dotenv
from logger import logger

# from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_core.utils.uuid import uuid7
from langchain_core.runnables import Runnable
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from definitions import DateTimeInput

load_dotenv()

calendar_service = CalendarService()


@tool
def view_calendar(start: DateTimeInput, end: DateTimeInput, limit: int | None):
    """Gets the events from the calendar in the specified range

    Args:
        start: the start of the range
        end: the end of the range
        limit: the number of results to return. default = 10, Use None for no limit.
    """

    logger.info(
        "Tool called | tool=get_busy_periods | start=%s | end=%s",
        parse_datetimeinput(start).isoformat(),
        parse_datetimeinput(end).isoformat(),
    )
    result = calendar_service.get_events(start, end, limit)
    is_result_success = not not result or type(result) is list
    if is_result_success:
        logger.info(
            "Tool completed | tool=get_busy_periods | success=%s | start=%s | end=%s | events=%s",
            is_result_success,
            parse_datetimeinput(start).isoformat(),
            parse_datetimeinput(end).isoformat(),
            len(result) if hasattr(result, "__len__") else "None",
        )
    else:
        logger.warning(
            "Tool completed | tool=get_busy_periods | success=%s | start=%s | end=%s | events=%s",
            is_result_success,
            parse_datetimeinput(start).isoformat(),
            parse_datetimeinput(end).isoformat(),
            len(result) if hasattr(result, "__len__") else "None",
        )
    return result


@tool
def get_event(event_id: str):
    """Get specific event details of an event by its ID

    Args:
        event_id: the event's id
    """

    logger.info("Tool called | tool=get_event | event_id=%s", event_id)
    result = calendar_service.get_event(event_id)
    is_result_success = not not result
    if is_result_success:
        logger.info("Tool completed | tool=get_event | success=%s", result)
    else:
        logger.warning("Tool completed | tool=get_event | success=%s", result)

    return result


@tool
def get_busy_periods(start: DateTimeInput, end: DateTimeInput):
    """Returns the periods where the user is occupied/busy within a specified range.

    Args:
        start: the start of the range
        end: the end of the range

    """
    logger.info(
        "Tool called | tool=get_busy_periods | start=%s | end=%s",
        parse_datetimeinput(start).isoformat(),
        parse_datetimeinput(end).isoformat(),
    )
    result = calendar_service.get_busy_periods(start, end)
    is_result_success = not not result or type(result) is list
    if is_result_success:

        logger.info(
            "Tool completed | tool=get_busy_periods | success=%s | start=%s | end=%s",
            is_result_success,
            parse_datetimeinput(start).isoformat(),
            parse_datetimeinput(end).isoformat(),
        )
    else:
        logger.warning(
            "Tool completed | tool=get_busy_periods | success=%s | start=%s | end=%s",
            is_result_success,
            parse_datetimeinput(start).isoformat(),
            parse_datetimeinput(end).isoformat(),
        )
    return result


@tool
def is_available(start: DateTimeInput, end: DateTimeInput) -> bool:
    """Returns whether the user is free for the entire duration of the specified range

    Args:
        start: the start of the range
        end: the end of the range

    """

    logger.info(
        "Tool called | tool=is_available | start=%s | end=%s",
        parse_datetimeinput(start).isoformat(),
        parse_datetimeinput(end).isoformat(),
    )
    result = calendar_service.is_available(start, end)
    is_result_success = True if result == True or result == False else False
    if is_result_success:
        logger.info(
            "Tool completed | tool=is_available | success=%s | start=%s | end=%s",
            is_result_success,
            parse_datetimeinput(start).isoformat(),
            parse_datetimeinput(end).isoformat(),
        )
    else:
        logger.warning(
            "Tool completed | tool=is_available | success=%s | start=%s | end=%s",
            is_result_success,
            parse_datetimeinput(start).isoformat(),
            parse_datetimeinput(end).isoformat(),
        )
    return result


@tool
def create_event(
    summary: str,
    start: DateTimeInput,
    end: DateTimeInput,
    description: str = None,
    location: str = None,
    recurrence: str = None,
):
    """Create and insert an event into the user's calendar

    Args:
        (required)
        summary: the event title
        start: the start date/time of the event
        end: the end date/time of the event

        (optional)
        description: extra details of the event
        location: where the event will take place
        recurrence: recurrence rule of the event (RFC-5545)

    """

    logger.info(
        "Tool called | tool=create_event | event_summary=%s | start=%s | end=%s",
        summary,
        parse_datetimeinput(start).isoformat(),
        parse_datetimeinput(end).isoformat(),
    )
    result = calendar_service.create_event(
        summary, start, end, description, location, recurrence
    )
    is_result_success = not not result
    if is_result_success:
        logger.info(
            "Tool completed | tool=create_event | event_summary=%s | success=%s",
            summary,
            is_result_success,
        )
    else:
        logger.warning(
            "Tool completed | tool=create_event | event_summary=%s | success=%s",
            summary,
            is_result_success,
        )
    return result


@tool
def update_event(
    event_id: str,
    summary: str = None,
    start: DateTimeInput = None,
    end: DateTimeInput = None,
    description: str = None,
    location: str = None,
):
    """Update an existing event by its ID, also passing the changed fields

    Args:
        (required)
        event_id: the event's id

        (optional)
        summary: the event title
        start: the start date/time of the event
        end: the end date/time of the event
        description: extra details of the event
        location: where the event will take place
    """
    logger.info("Tool called | tool=update_event | event_id=%s", event_id)
    result = calendar_service.update_event(
        event_id, summary, start, end, description, location
    )
    is_result_success = not not result
    if is_result_success:
        logger.info(
            "Tool completed | tool=update_event | success=%s", is_result_success
        )
    else:
        logger.warning(
            "Tool completed | tool=update_event | success=%s", is_result_success
        )
    return result


@tool
def delete_event(event_id: str) -> bool:
    """Delete an event by its ID

    Args:
        event_id: the event's id
    """
    logger.info("Tool called | tool=delete_event | event_id=%s", event_id)
    result = calendar_service.delete_event(event_id)
    is_result_success = not not result
    if is_result_success:
        logger.info("Tool completed | tool=delete_event | success=%s", result)
    else:
        logger.warning("Tool completed | tool=delete_event | success=%s", result)
    return result


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    print("""Welcome to your personal calendar assistant!""")

    # llm = ChatOllama(model="qwen3:8b", num_ctx=8192)
    model = ChatOpenAI(
        model="gpt-5-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=os.environ.get("OPENAI_API_KEY"),
        # base_url="...",
        # organization="...",
        # other params...
    )
    checkpointer = InMemorySaver()

    system_prompt = """
    You are a personal calendar assistant.

    Help the user view, check, create, update, and delete events in their Google Calendar.

    ## Rules

    * Use calendar tools whenever you need information from or need to make changes to the user's calendar.
    * Use read-only tools such as `get_events` and `is_available` freely.
    * Clearly state the intent and the parameters when using calendar-changing tools such as `create_event`, `update_event`, and `delete_event`, but never ask for user approval.
    * Never claim an event was created, updated, or deleted unless the tool successfully completes the operation.
    * Do not invent events, availability, event IDs, or tool results.
    * When modifying or deleting an existing event, make sure you have identified the correct event.
    * If the user's request is ambiguous or missing important information required to complete it, ask for clarification.
    * If the user does not provide optional parameters, assume they do not want to provide them.
    * Do not invite people to events.
    * When scheduling an event, check its availability when appropriate before creating it.
    * Treat relative dates such as "tomorrow" and "next Tuesday" according to the current date/time provided by the system.
    * Be concise and natural.

    """

    agent: Runnable = create_agent(
        model=model,
        tools=[
            view_calendar,
            get_event,
            get_busy_periods,
            is_available,
            create_event,
            update_event,
            delete_event,
        ],
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "create_event": True,
                    "update_event": True,
                    "delete_event": True,
                    "view_calendar": False,
                    "get_event": False,
                    "get_busy_periods": False,
                    "is_available": False,
                }
            ),
        ],
        system_prompt=system_prompt,
        checkpointer=checkpointer,
    )

    thread_id = str(uuid7())
    config = {"configurable": {"thread_id": thread_id}}
    logger.info("Agent started | thread=%s", thread_id)
    while True:

        state = agent.get_state(config)

        if state.interrupts:
            interrupt_action = state.interrupts[0].value["review_configs"][0][
                "action_name"
            ]
            action_requests = state.interrupts[0].value["action_requests"]

            logger.info(
                "HITL interrupt | thread_id=%s | action=%s | pending_actions=%s",
                thread_id,
                interrupt_action,
                len(action_requests),
            )

            user_input = input("Please approve (yes/no): ")

            if user_input == "q":
                break

            user_decision = user_input.lower().strip()

            print(len(state.interrupts))

            if user_decision in ["yes", "y", "approve", "approved"]:
                logger.info(
                    "HITL decision | thread_id=%s | action=%s | decision=approve",
                    thread_id,
                    interrupt_action,
                )
                resume_value = {"decisions": [{"type": "approve"}]}

            elif user_decision in ["no", "n", "reject", "rejected"]:
                logger.warning(
                    "HITL decision | thread_id=%s | action=%s | decision=reject",
                    thread_id,
                    interrupt_action,
                )
                resume_value = {"decisions": [{"type": "reject"}]}

            else:
                print("Please enter yes or no.")
                continue

            stream = agent.stream_events(
                Command(resume=resume_value),
                config=config,
                version="v3",
            )

        else:
            print("\n")
            print("(q to quit)\nEnter message: ")
            user_input = input()

            if user_input == "q":
                break

            stream = agent.stream_events(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                version="v3",
            )

        for kind, item in stream.interleave("messages", "tool_calls"):
            if kind == "messages":
                for token in item.text:
                    print(token, end="", flush=True)

            elif kind == "tool_calls":

                print(f"\nTool call: {item.tool_name}({item.input})")
                for delta in item.output_deltas:
                    print(delta, end="", flush=True)
                print(f"\nTool result: {item.output}")

        state = agent.get_state(config)

        if state.interrupts:
            continue

        final_state = stream.output


if __name__ == "__main__":
    main()
