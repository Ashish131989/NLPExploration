from laya import Router
from pprint import pprint


# ============================================================
# CONFIGURATION
# ============================================================

CONFIDENCE_THRESHOLD = 0.70

print("=" * 70)
print("INSURANCE MULTI-GOAL ORCHESTRATOR - LAYA POC")
print("=" * 70)

print("\nLoading Laya...")

# Keep your existing working configuration
router = Router(default="multilingual")

print("Laya loaded successfully!")


# ============================================================
# CUSTOMER INPUT
# ============================================================

customer_message = (
    "I had an accident and need to file a claim. "
    "I also need a rental car because my vehicle cannot be driven."
)

state = {
    "subject": "Insurance customer request",
    "body": customer_message,
}


# ============================================================
# GOAL DEFINITIONS
# ============================================================

GOALS = {
    "claim": {
        "description": (
            "The customer wants to report an accident, "
            "report damage, or file an insurance claim."
        ),
        "agent": "ClaimsAgent",
    },

    "rental": {
        "description": (
            "The customer needs or wants a rental vehicle, "
            "rental car, or temporary replacement vehicle."
        ),
        "agent": "RentalAgent",
    },

    "roadside": {
        "description": (
            "The customer needs roadside assistance, towing, "
            "jump start, tire assistance, lockout help, or "
            "vehicle breakdown assistance."
        ),
        "agent": "RoadsideAgent",
    },

    "billing": {
        "description": (
            "The customer has a payment, premium, billing, "
            "charge, refund, or invoice issue."
        ),
        "agent": "BillingAgent",
    },

    "policy": {
        "description": (
            "The customer wants policy information, "
            "policy changes, coverage information, "
            "or policy documents."
        ),
        "agent": "PolicyAgent",
    },

    "id_card": {
        "description": (
            "The customer needs an insurance ID card, "
            "proof of insurance, or insurance card."
        ),
        "agent": "IDCardAgent",
    },
}


# ============================================================
# BUILD MULTI-GOAL QUESTIONS
# ============================================================

questions = {}

for goal_name, goal_config in GOALS.items():

    questions[f"needs_{goal_name}"] = {
        "type": "noul",

        "instructions": (
            f"Does the customer have this insurance goal: "
            f"{goal_config['description']}"
        ),
    }


# ============================================================
# CALL LAYA
# ============================================================

print("\nAnalyzing customer request...\n")

result = router.predict(
    state,
    questions
)


# ============================================================
# DEBUG - RAW RESULT
# ============================================================

print("=" * 70)
print("RAW LAYA RESULT")
print("=" * 70)

pprint(result)


# ============================================================
# EXTRACT ANSWERS
# ============================================================

answers = result.get("answers", {})

print("\n" + "=" * 70)
print("GOAL DETECTION")
print("=" * 70)


detected_goals = []


for goal_name in GOALS.keys():

    question_name = f"needs_{goal_name}"

    answer = answers.get(question_name)

    if answer is None:
        print(f"\n{goal_name.upper():12} -> NO RESULT")
        continue

    # Laya's noul result
    probability = answer.get("noul", 0.0)

    is_goal = probability >= CONFIDENCE_THRESHOLD

    print(
        f"\n{goal_name.upper():12} "
        f"-> {'YES' if is_goal else 'NO '} "
        f"({probability:.2%})"
    )

    if is_goal:

        detected_goals.append({
            "goal": goal_name,
            "confidence": probability,
            "agent": GOALS[goal_name]["agent"],
        })


# ============================================================
# ORDER DETECTION
# ============================================================

print("\n" + "=" * 70)
print("DETECTED GOALS")
print("=" * 70)


if not detected_goals:

    print("\nNo goals detected.")

else:

    for index, goal in enumerate(detected_goals, start=1):

        goal["order"] = index

        print(
            f"{index}. "
            f"{goal['goal'].upper()} "
            f"| confidence={goal['confidence']:.2%} "
            f"| agent={goal['agent']}"
        )


# ============================================================
# IMPORTANT:
# ============================================================
#
# Laya's independent NOUL questions tell us whether each
# proposition is true.
#
# They do NOT reliably tell us the textual order in which
# multiple goals appeared.
#
# Therefore this POC initially preserves the configured goal
# order.
#
# Later we can add a dedicated "goal_order" decision or
# lightweight span/order extraction.
#
# For the first POC, use this deterministic business order:
#
# CLAIM -> RENTAL -> ROADSIDE -> BILLING -> POLICY -> ID CARD
#
# ============================================================


GOAL_EXECUTION_ORDER = [
    "claim",
    "rental",
    "roadside",
    "billing",
    "policy",
    "id_card",
]


def sort_goals_for_execution(goals):

    order_map = {
        goal: index
        for index, goal in enumerate(GOAL_EXECUTION_ORDER)
    }

    return sorted(
        goals,
        key=lambda item: order_map.get(
            item["goal"],
            999
        )
    )


detected_goals = sort_goals_for_execution(
    detected_goals
)


# ============================================================
# ORCHESTRATOR STATE
# ============================================================

orchestrator_state = {

    "customer_message": customer_message,

    "detected_goals": detected_goals,

    "current_goal": None,

    "completed_goals": [],

    "failed_goals": [],

    "results": [],
}


# ============================================================
# MOCK INSURANCE AGENTS
# ============================================================

def claims_agent(state):

    print("\n----------------------------------------")
    print("CLAIMS AGENT")
    print("----------------------------------------")

    print("Claims Agent received customer request.")

    # Replace this later with actual Claims Agent logic
    result = {
        "status": "completed",
        "message": "Claim intake completed.",
    }

    return result


def rental_agent(state):

    print("\n----------------------------------------")
    print("RENTAL AGENT")
    print("----------------------------------------")

    print("Rental Agent received customer request.")

    # Replace this later with actual Rental Agent logic
    result = {
        "status": "completed",
        "message": "Rental vehicle request processed.",
    }

    return result


def roadside_agent(state):

    print("\n----------------------------------------")
    print("ROADSIDE AGENT")
    print("----------------------------------------")

    print("Roadside Agent received customer request.")

    result = {
        "status": "completed",
        "message": "Roadside assistance request processed.",
    }

    return result


def billing_agent(state):

    print("\n----------------------------------------")
    print("BILLING AGENT")
    print("----------------------------------------")

    print("Billing Agent received customer request.")

    result = {
        "status": "completed",
        "message": "Billing request processed.",
    }

    return result


def policy_agent(state):

    print("\n----------------------------------------")
    print("POLICY AGENT")
    print("----------------------------------------")

    print("Policy Agent received customer request.")

    result = {
        "status": "completed",
        "message": "Policy request processed.",
    }

    return result


def id_card_agent(state):

    print("\n----------------------------------------")
    print("ID CARD AGENT")
    print("----------------------------------------")

    print("ID Card Agent received customer request.")

    result = {
        "status": "completed",
        "message": "ID card request processed.",
    }

    return result


# ============================================================
# AGENT REGISTRY
# ============================================================

AGENTS = {

    "claim": claims_agent,

    "rental": rental_agent,

    "roadside": roadside_agent,

    "billing": billing_agent,

    "policy": policy_agent,

    "id_card": id_card_agent,
}


# ============================================================
# EXECUTE ONE GOAL
# ============================================================

def execute_goal(goal):

    goal_name = goal["goal"]

    agent_name = goal["agent"]

    print("\n" + "=" * 70)
    print(
        f"EXECUTING GOAL #{goal['order']}: "
        f"{goal_name.upper()}"
    )
    print("=" * 70)

    print(
        f"Agent       : {agent_name}"
    )

    print(
        f"Confidence  : {goal['confidence']:.2%}"
    )

    agent = AGENTS.get(goal_name)

    if agent is None:

        print(
            f"No agent registered for {goal_name}"
        )

        return {
            "status": "failed",
            "message": "Agent not found.",
        }

    try:

        result = agent(orchestrator_state)

        return result

    except Exception as error:

        print(
            f"Agent execution error: {error}"
        )

        return {
            "status": "failed",
            "message": str(error),
        }


# ============================================================
# MULTI-GOAL ORCHESTRATOR
# ============================================================

def run_orchestrator():

    print("\n\n")
    print("#" * 70)
    print("STARTING MULTI-GOAL EXECUTION")
    print("#" * 70)

    if not detected_goals:

        print("\nNothing to execute.")

        return

    for goal in detected_goals:

        orchestrator_state["current_goal"] = goal

        print(
            f"\nCurrent goal: "
            f"{goal['goal'].upper()}"
        )

        result = execute_goal(goal)

        orchestrator_state["results"].append({

            "goal": goal["goal"],

            "result": result,

        })

        if result["status"] == "completed":

            orchestrator_state[
                "completed_goals"
            ].append(
                goal["goal"]
            )

            print(
                f"\n✓ {goal['goal'].upper()} completed"
            )

        else:

            orchestrator_state[
                "failed_goals"
            ].append(
                goal["goal"]
            )

            print(
                f"\n✗ {goal['goal'].upper()} failed"
            )


        # ----------------------------------------------------
        # Important:
        #
        # We continue to the next goal.
        #
        # In the real implementation, this is where we can
        # decide whether the next agent should execute based
        # on the previous agent's result.
        # ----------------------------------------------------


    orchestrator_state["current_goal"] = None


# ============================================================
# RUN
# ============================================================

run_orchestrator()


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n\n")
print("#" * 70)
print("FINAL ORCHESTRATOR STATE")
print("#" * 70)

print(
    "\nCustomer:"
)

print(
    orchestrator_state["customer_message"]
)


print("\nDetected goals:")

for goal in orchestrator_state["detected_goals"]:

    print(
        f"  {goal['order']}. "
        f"{goal['goal']} "
        f"({goal['confidence']:.2%})"
    )


print("\nCompleted goals:")

for goal in orchestrator_state["completed_goals"]:

    print(
        f"  ✓ {goal}"
    )


print("\nFailed goals:")

for goal in orchestrator_state["failed_goals"]:

    print(
        f"  ✗ {goal}"
    )


print("\n" + "=" * 70)
print("POC COMPLETE")
print("=" * 70)