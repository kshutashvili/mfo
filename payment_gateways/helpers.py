import re
from datetime import date

import telepot

from django.conf import settings

from payment_gateways.utils import create_database_connection


def search_credit(cursor, contract_num):
    """
    Return matched credit data

    Positions in tuple:
    0 - Credit ID
    1 - Client ID
    2 - Client names
    3 - Credit vnoska
    4 - Credit status (must be 5)
    5 - Client IPN
    """
    try:
        cursor.execute(
            """
                SELECT
                    tc.id,
                    tc.client_id,
                    concat(tp.name3, ' ', tp.name, ' ', tp.name2),
                    tc.vnoska,
                    ts.status,
                    tc.egn
                FROM
                    mbank.tcredits tc
                join mbank.tstatuses ts on ts.credit_id = tc.id
                                       and ts.is_last = 1
                join mbank.tpersons tp on tp.id = tc.client_id
                WHERE tc.contract_num = {0}
                  and ts.status = 5;
            """.format(contract_num)
        )
    except Exception:
        return None

    credit = cursor.fetchall()

    if credit:
        return credit

    return None


def save_payment(conn, cursor, data):
    """
    Save payment in in_razpredelenie table
    in DB Turnes.
    """
    query = """
        INSERT INTO
        in_razpredelenie (
            No, DogNo, IPN, F, I, O,
            dt, sm, status, ibank
        )
        VALUES (
            '{0}', '{1}', '{2}',
            '{3}', '{4}', '{5}',
            '{6}', {7}, {8},
            '{9}'
        );
    """.format(
        data["No"], data["DogNo"], data["IPN"],
        data["F"], data["I"], data["O"],
        data["dt"], data["sm"], data["status"],
        data["ibank"]
    )
    try:
        cursor.execute(query)
    except Exception as e:
        raise e

    conn.commit()  # submit inserting
    return cursor.lastrowid


def run_payments_distribution(pay_date=None):
    """
        Execute RunRazpredelenie function
        in Turnes DB. Distribute payment by pay_date
        or today date.
    """

    try:
        conn, cursor = create_database_connection(
            host=settings.TURNES_HOST,
            user=settings.TURNES_USER,
            password=settings.TURNES_PASSWORD,
            db=settings.TURNES_DATABASE
        )
    except Exception:
        return None

    if pay_date:
        # check required format ('1999-01-31')
        regex = re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})$", pay_date)
        if regex:
            q = cursor.execute(
                """
                select mbank.RunRazpredelenie('{0}');
                """.format(pay_date)
            )
        else:
            conn.close()
            raise Exception("Invalid date format. Must be 'YYYY-MM-DD'")
    else:
        q = cursor.execute(
            """
            select mbank.RunRazpredelenie('{0}');
            """.format(
                date.today().strftime('%Y-%m-%d')
            )
        )

        conn.close()

        # q = cursor.execute(
        #     """
        #     select mbank.RunRazpredelenie('');
        #     """
        # )


def telegram_notification(err='', message=''):
    """
        Send fail messages to telegram group
    """
    # success \U00002705
    # fail \U0000274C
    try:
        # try authenticate bot
        test_bot = telepot.Bot(settings.TEST_API_KEY)
    except Exception:
        # if connection is not established, do nothing
        return

    test_bot.sendMessage(
        settings.TEST_GROUP_ID,
        "\U0000274C{0}\n{1}".format(
            err,
            message
        )
    )
