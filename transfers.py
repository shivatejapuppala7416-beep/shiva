from flask import Blueprint, request, jsonify
from database.db import get_connection
import mysql.connector


transfers_bp = Blueprint(
    "transfers",
    __name__
)


@transfers_bp.post("/create")
def create_transfer():

    data = request.get_json(silent=True) or {}

    print("\n==============================")
    print("TRANSFER REQUEST RECEIVED")
    print(data)
    print("==============================\n")

    # -----------------------------
    # Validate required fields
    # -----------------------------

    required_fields = [
        "user_id",
        "sender_wallet",
        "recipient_wallet",
        "amount",
        "destination",
        "selected_route",
        "transaction_hash"
    ]

    for field in required_fields:

        if data.get(field) in [None, ""]:

            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = None
    cursor = None

    try:

        # -----------------------------
        # Connect to MySQL
        # -----------------------------

        connection = get_connection()

        cursor = connection.cursor()

        # -----------------------------
        # INSERT INTO transfers
        # -----------------------------

        query = """
        INSERT INTO transfers
        (
            user_id,
            sender_wallet,
            recipient_wallet,
            amount,
            destination,
            selected_route,
            fee,
            exchange_rate,
            estimated_minutes,
            amount_received,
            ai_reason,
            transaction_hash,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        values = (
            int(data["user_id"]),

            data["sender_wallet"],

            data["recipient_wallet"],

            float(data["amount"]),

            data["destination"],

            data["selected_route"],

            float(data.get("fee", 0)),

            float(
                data.get(
                    "exchange_rate",
                    0
                )
            ),

            int(
                data.get(
                    "estimated_minutes",
                    0
                )
            ),

            float(
                data.get(
                    "amount_received",
                    0
                )
            ),

            data.get(
                "ai_reason",
                ""
            ),

            data["transaction_hash"],

            data.get(
                "status",
                "PENDING"
            )
        )

        # -----------------------------
        # Execute INSERT
        # -----------------------------

        cursor.execute(
            query,
            values
        )

        # -----------------------------
        # COMMIT
        # -----------------------------

        connection.commit()

        transfer_id = cursor.lastrowid

        print(
            "✅ TRANSFER SAVED"
        )

        print(
            "Transfer ID:",
            transfer_id
        )

        print(
            "Transaction Hash:",
            data["transaction_hash"]
        )

        # -----------------------------
        # Response
        # -----------------------------

        return jsonify({

            "success": True,

            "message":
                "Transfer saved successfully",

            "transfer_id":
                transfer_id,

            "transaction_hash":
                data["transaction_hash"],

            "status":
                data.get(
                    "status",
                    "PENDING"
                )

        }), 201

    except mysql.connector.Error as e:

        if connection:
            connection.rollback()

        print(
            "❌ MYSQL ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                "MySQL error",

            "details":
                str(e)

        }), 500

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "❌ TRANSFER ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                "Transfer save failed",

            "details":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()