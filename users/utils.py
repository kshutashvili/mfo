from pprint import pprint
from datetime import datetime

import MySQLdb

from payments.models import Payment


def test_user_turnes(turnes_id):
    if not turnes_id:
        return None

    exfin_connection = MySQLdb.connect(
        host="10.10.100.27",                # host of MySQL database
        user="root",                        # user's username
        passwd="Orraveza(99)",              # your password
        db="mbank",                         # name of the database
        charset="utf8"
    )

    # create CURSOR and set UTF8 params
    exfin_cursor = exfin_connection.cursor()
    exfin_cursor.execute('SET NAMES utf8;')
    exfin_cursor.execute('SET CHARACTER SET utf8;')
    exfin_cursor.execute('SET character_set_connection=utf8;')

    """
        SQL Query from table mbank.tpersons

        FIELDS
        0: id of record
        1: id of state (oblast) from passwort       -- lk_adr_oblast
        2: name of region (rayon) from passport     -- lk_adr_obsh
        3: name of city (gorod) from passport       -- lk_adr_city
        4: name of street (ulica) from passport     -- lk_adr_ul
        5: number of building (dom) from passport   -- lk_adr_num
        6: number of flat (kvartira) from passport  -- lk_adr_ap
        7: id of mobile operator                    -- tel_mob_kod
        8: number of mobile phone (w/o +38 and code)-- tel_mob_num
        9: email
        10: first name                              -- name
        11: middle name                             -- name2
        12: last name                               -- name3
        13: ITN (Individual Tax-payer Number)       -- egn
    """
    exfin_cursor.execute(
        """
            SELECT
                id,
                lk_adr_oblast,
                lk_adr_obsh,
                lk_adr_city,
                lk_adr_ul,
                lk_adr_num,
                lk_adr_ap,
                tel_mob_kod,
                tel_mob_num,
                email,
                name,
                name2,
                name3,
                egn
            FROM
                mbank.tpersons
            WHERE id = {0};
        """.format(int(turnes_id))  # 144580
    )
    person_data = exfin_cursor.fetchall()[0]

    """
        SQL Query from table mbank.fvalues

        FIELDS
        0: birthday date                    -- val
    """
    exfin_cursor.execute(
        """
            SELECT
                val
            FROM
                mbank.fvalues
            WHERE corrid = {0} and code = 'bdate';
        """.format(person_data[0])
    )
    person_birthday = exfin_cursor.fetchall()[0]

    """
        SQL Query from table mbank.fvalues

        FIELDS
        0: name of birthday city               -- val
    """
    exfin_cursor.execute(
        """
            SELECT
                val
            FROM
                mbank.fvalues
            WHERE corrid = {0} and code = 'bplace';
        """.format(person_data[0])
    )
    person_birthday_place = exfin_cursor.fetchall()[0]

    """
        SQL Query from table mbank.tdropdown_details

        FIELDS
        0: mobile operator code               -- name
    """
    exfin_cursor.execute(
        """
            SELECT
                name
            FROM
                mbank.tdropdown_details
            WHERE id = {0};
        """.format(person_data[7])
    )
    person_mobile_operator_code = exfin_cursor.fetchall()[0]

    """
        SQL Query from table mbank.tdropdown_details

        FIELDS
        0: name of state (oblast)               -- name
    """
    exfin_cursor.execute(
        """
            SELECT name
            from mbank.tdropdown_details
            where dropdown=2 and id = {0}
        """.format(person_data[1])
    )
    person_oblast = exfin_cursor.fetchall()[0]

    """
        SQL Query from table mbank.lists

        FIELDS
        0: street type               -- listname
    """
    exfin_cursor.execute(
        """
            SELECT
                lists.listname
            FROM
                mbank.fvalues fval
            join
                (
                    select listname, listcode, listval
                    from mbank.lists
                ) lists on lists.listcode = fval.listcode
                       and lists.listval = fval.val
            WHERE
                corrid = {0}
            and code = 'Street_type_reg';
        """.format(person_data[0])
    )
    person_street_type = exfin_cursor.fetchall()[0]

    """
        SQL Query from table mbank.tcredits

        FIELDS
        0: credit ID                                    -- id
        1: amount of each pay                           -- vnoska
        2: loan sum (suma credita)                      -- suma
        3: ITN (Individual Tax-payer Number)            -- egn
        4: credit contract date                         -- contract_date
        5: credit contract num (nomer dogovora)         -- contract_num
        6: number of pays                               -- number_of_pays
        7: sum which crient will pay (suma + %)         -- full_sum
        8: how much client already paid                 -- already_paid
        9: how much is left to pay                      -- rest_pays_sum
        10: how many payments remain                    -- number_of_rest_pays
        11: last day of credit                          -- last_pay_date
        12: code of credit status                       -- status
    """
    exfin_cursor.execute(
        """
            SELECT
                tcr.id,
                tcr.vnoska,
                tcr.suma,
                tcr.egn,
                tcr.contract_date,
                tcr.contract_num,

                pays_calendar.number_of_pays,
                pays_calendar.full_sum,
                pays_calendar.already_paid,
                pays_calendar.rest_pays_sum,
                pays_calendar.number_of_rest_pays,
                pays_calendar.last_pay_date,
                tst.status
            FROM
                mbank.tcredits tcr
            left join(
                SELECT
                    tpp_main.id,
                    tpp_main.credit_id,
                    count(*) as number_of_pays,
                    sum(tpp_main.sum) as full_sum,
                    ifnull(tpp_join.already_paid, 0) as already_paid,
                    sum(tpp_main.sum) - ifnull(tpp_join.already_paid, 0) as rest_pays_sum,
                    count(*) - tpp_join.paid_pays as number_of_rest_pays,
                    date(max(tpp_main.data)) as last_pay_date
                FROM
                    mbank.tpp tpp_main
                LEFT join
                (
                    select id, sum(sum) as already_paid, count(*) as paid_pays
                    from mbank.tpp
                    where ispaid = 1
                    group by credit_id
                ) tpp_join on tpp_join.id = tpp_main.id
                group by tpp_main.credit_id
            ) pays_calendar on pays_calendar.credit_id = tcr.id

            join mbank.tstatuses tst on tst.credit_id = tcr.id and tst.status = 5 and tst.credit_id not in (
                select tst11.credit_id from mbank.tstatuses tst11 
                where tst11.status in (11, 111)
            )
            WHERE
                tcr.egn = {0} and tcr.is_otpusnat = 1;
        """.format(person_data[13])
    )
    person_credits = exfin_cursor.fetchall()

    credits = []
    for credit in person_credits:
        # exfin_cursor.execute(
        #     """
        #         SELECT max(dt) last_date, dolg_all, crd_id
        #         from dwh.credits_saldo
        #         where crd_id = {0}
        #         group by crd_id
        #     """.format(credit[0])
        # )
        # credit_dolg = exfin_cursor.fetchall()

        """
            SQL Query from table mbank.tpp

            tpp is table with calendar of pays to credit

            FIELDS
            0: tpp ID                                   -- id
            1: credit ID of tpp                         -- credit_id
            2: pay sum (= vnoska from tcredits)         -- sum
            3: date after which the debt will grow      -- data
            4: will be paid or no (1 or 0)              -- ispaid
        """
        exfin_cursor.execute(
            """
                SELECT
                    id,
                    credit_id,
                    sum,
                    data,
                    ispaid
                from mbank.tpp
                where credit_id = {0}
            """.format(credit[0])
        )
        credit_tpp = exfin_cursor.fetchall()

        tpp_data_list = []
        pay_sums = []
        dolg_sums = []
        rest_sums = []
        tpp_pay_sums = []
        for i, tpp in enumerate(credit_tpp):
            try:
                """
                    SQL Query from table mbank.tcash

                    calculate sum of all pays which payed
                    between two calendar pays

                    FIELDS
                    0: how many paid between two calendar pays  -- how_paid
                    1: with which credit this sum is bound      -- iscredit
                    2: datetime of pays                         -- vreme
                """
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'in'
                          and nomenclature = 4
                          and iscredit = {0}
                          and date(vreme) between '{1}' and '{2}'
                        group by iscredit
                    """.format(credit[0], tpp[3], credit_tpp[i + 1][3])
                )
            except Exception:
                """
                    SQL Query from table mbank.tcash

                    if calendar pay is last, calculate pays sum
                    which datetime greatest than vreme field

                    FIELDS
                    0: how many paid between two calendar pays  -- how_paid
                    1: with which credit this sum is bound      -- iscredit
                    2: datetime of pays                         -- vreme
                """
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'in'
                          and nomenclature = 4
                          and iscredit = {0}
                          and date(vreme) > '{1}'
                        group by iscredit
                    """.format(credit[0], tpp[3])
                )
            tcash_in_sum = exfin_cursor.fetchall()

            try:
                """
                    SQL Query from table mbank.tcash

                    calculate dolg sum between two calendar pays

                    FIELDS
                    0: how many debt (dolg) between two pays    -- how_paid
                    1: with which credit this sum is bound      -- iscredit
                    2: datetime of pays                         -- vreme
                """
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'out'
                          and nomenclature = 7
                          and iscredit = {0}
                          and date(vreme) between '{1}' and '{2}'
                        group by iscredit
                    """.format(credit[0], tpp[3], credit_tpp[i + 1][3])
                )
            except Exception:
                """
                    SQL Query from table mbank.tcash

                    if calendar pay is last, starts calculate dolg
                    from last calendar pay vreme field

                    FIELDS
                    0: how many debt (dolg)                     -- how_paid
                    1: with which credit this sum is bound      -- iscredit
                    2: datetime of pays                         -- vreme
                """
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'out'
                          and nomenclature = 7
                          and iscredit = {0}
                          and date(vreme) > '{1}'
                        group by iscredit
                    """.format(credit[0], tpp[3])
                )
            tcash_dolg_sum = exfin_cursor.fetchall()

            """
            set calculated sum of pays (sum(sum) from mbank.tcash)
            if pays were not made (returned NULL) then set 0
            """
            pay_sum = tcash_in_sum[0][0] if tcash_in_sum else 0
            # save this sum in list for operating them later
            pay_sums.append(pay_sum)

            """
            set claculated debt(dolg) (sum(sum) from mbank.tcash)
            if client has not debt (returned NULL) then set 0
            """
            dolg_sum = tcash_dolg_sum[0][0] if tcash_dolg_sum else 0
            # save this sum in list for operating them later
            dolg_sums.append(dolg_sum)

            """
            calculate how much is left to pay
            substract sum of all dolg sums and
            sum of all already paid sums
            from full sum of credit
            """
            rest_sum = credit[7] - sum(dolg_sums) - sum(pay_sums)
            # save this sum in list for operating them later
            rest_sums.append(rest_sum)

            # check if user paid this calendar pay in this site
            tpp_ispaid = Payment.objects.filter(
                tpp_id=tpp[0],
                status=Payment.SUCCESS
            ).exists()

            # sum w/o tpp amount from Payment
            # rest_sum_finally = rest_sums[i-1] if i > 0 else credit[7] - dolg_sum

            """
            if calendar pay is first:
                calculate how much is left to pay finally
                subctract sum of pays made in this site
                and debt (dolg) for this calendar pay
                from full sum of credit
            else:
                calculate how much is left to pay finally
                subctract sum of pays made in this site
                and debt (dolg) for this calendar pay
                from previous rest sum
            """
            rest_sum_finally = float(rest_sums[i-1]) - sum(tpp_pay_sums) - dolg_sum if i > 0 else credit[7] - dolg_sum - sum(tpp_pay_sums)

            if tpp_ispaid:
                # get amount of calendar pay
                tpp_amount = Payment.objects.filter(
                    tpp_id=tpp[0],
                    status=Payment.SUCCESS
                )[0].amount
                # convert from kopeks to hryvnas
                tpp_pay_sums.append(float(tpp_amount) / 100)

            tpp_data_list.append(
                {
                    "id": tpp[0],
                    "date": tpp[3],
                    # "pay_sum": pay_sum,
                    "dolg_sum": -dolg_sum,
                    "ispaid": tpp[4] or tpp_ispaid,
                    "sum_must_pay": float(tpp[2]) - float(dolg_sum),
                    "rest_sum": rest_sum_finally
                }
            )

        credits.append(
            {
                # "pay_step": credit[1],
                "sum": credit[2],
                "contract_date": credit[4].strftime("%d.%m.%Y"),
                "contract_num": credit[5],
                # "number_of_pays": credit[6],
                # "full_sum": credit[7],
                # "already_paid": credit[8],
                # "rest_pays_sum": credit[9],
                # "number_of_rest_pays": credit[10],
                # "last_pay_date": credit[11].strftime("%d.%m.%Y"),
                # "dolg": credit_dolg[0][1],
                # "pay_step_with_dolg": credit[1] + credit_dolg[0][1],
                "tpp": tpp_data_list
            }
        )
    # pprint(credits)

    return {
        "names": " ".join([
            person_data[12],
            person_data[10],
            person_data[11]
        ]),
        "address": "{0} обл., {1} район, {2}, {3} {4}, {5}, кв.{6}".format(
            person_oblast[0],
            person_data[2],
            person_data[3],
            person_street_type[0],
            person_data[4],
            person_data[5],
            person_data[6]
        ),
        "email": person_data[9],
        "birthday_place": person_birthday_place[0],
        "birthday": datetime.strptime(person_birthday[0], "%Y-%m-%d").strftime("%d.%m.%Y"),
        "mobile_phone": " ".join([
            person_mobile_operator_code[0],
            person_data[8]
        ]),
        "credits": credits
    }


def get_person_id(contract_num, phone):
    """
        Get person's ID from mbank.tcredits (turnes DB)
    """
    exfin_connection = MySQLdb.connect(
        host="10.10.100.27",                # host of MySQL database
        user="root",                        # user's username
        passwd="Orraveza(99)",              # your password
        db="mbank",                         # name of the database
        charset="utf8"
    )

    # create CURSOR and set UTF8 params
    exfin_cursor = exfin_connection.cursor()
    exfin_cursor.execute('SET NAMES utf8;')
    exfin_cursor.execute('SET CHARACTER SET utf8;')
    exfin_cursor.execute('SET character_set_connection=utf8;')

    exfin_cursor.execute(
        """
            SELECT
                tc.id,
                tc.client_id,
                ts.status as last_status,
                ts.dt_created,
                tp.tel_mob_num
            FROM
                mbank.tcredits tc
            join mbank.tstatuses ts on ts.credit_id = tc.id
            join mbank.tpersons tp on tp.id = tc.client_id
            WHERE tc.contract_num =  {0}
            ORDER BY ts.dt_created DESC
            LIMIT 1;
        """.format(contract_num)
    )
    person_id = exfin_cursor.fetchall()

    try:
        """
            if credit status == 5 return client's ID
            status 5 is 'active credit'
            and
            if phone contain tel_mob_num
        """
        if person_id[0][2] in [5, '5'] and person_id[0][4] in phone:
            return person_id[0][1]
        else:
            return ""
    except IndexError:
        return ""


def get_person_id_and_tel(contract_num):
    """
        Get person's ID from mbank.tcredits (turnes DB)
    """
    exfin_connection = MySQLdb.connect(
        host="10.10.100.27",                # host of MySQL database
        user="root",                        # user's username
        passwd="Orraveza(99)",              # your password
        db="mbank",                         # name of the database
        charset="utf8"
    )

    # create CURSOR and set UTF8 params
    exfin_cursor = exfin_connection.cursor()
    exfin_cursor.execute('SET NAMES utf8;')
    exfin_cursor.execute('SET CHARACTER SET utf8;')
    exfin_cursor.execute('SET character_set_connection=utf8;')

    exfin_cursor.execute(
        """
            SELECT
                tc.id,
                tc.client_id,
                ts.status as last_status,
                ts.dt_created,
                tp.tel_mob_num,
                tp.tel_mob_kod
            FROM
                mbank.tcredits tc
            join mbank.tstatuses ts on ts.credit_id = tc.id
            join mbank.tpersons tp on tp.id = tc.client_id
            WHERE tc.contract_num =  {0}
            ORDER BY ts.dt_created DESC
            LIMIT 1;
        """.format(contract_num)
    )
    person_data = exfin_cursor.fetchall()

    if person_data[0]:
        exfin_cursor.execute(
            """
                SELECT
                    name
                FROM
                    mbank.tdropdown_details
                WHERE id = {0};
            """.format(person_data[0][5])
        )
        person_mobile_operator_code = exfin_cursor.fetchall()[0]

        try:
            """
                if client_id and tel_mob_num exists
            """
            if person_data[0][1] and person_data[0][4]:
                print(
                    "get_person_id_and_tel",
                    "+38{0}{1}".format(
                        person_mobile_operator_code[0],
                        person_data[0][4]
                    )
                )
                return (
                    person_data[0][1],
                    "+38{0}{1}".format(
                        person_mobile_operator_code[0],
                        person_data[0][4]
                    )
                )
            else:
                return ""
        except IndexError:
            return ""
    else:
        return ""
