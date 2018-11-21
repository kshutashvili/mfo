import base64
import re
from pprint import pprint
from datetime import datetime
from io import BytesIO

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import requests

from django.core import files
from django.conf import settings

from users.models import Questionnaire
from .models import (
    Customer, Document, Address, ScanDocument,
    BankIDLog
)


def decrypt_data(encrypted_data):
    # print("decrypt_data")
    # print(encrypted_data)
    BankIDLog.objects.create(
        type='DecryptData',
        subtype="encrypted_data",
        message=encrypted_data
    )
    # import private key which should use for decryption
    if settings.DEBUG:
        priv = RSA.importKey(
            open('/home/phonxis/rsa_key.pem', 'rb').read(),
            passphrase='4602161'
        )
    else:
        priv = RSA.importKey(
            open('/var/sites/e-fin/key_for_bankid/rsa_key.pem', 'rb').read(),
            passphrase='4602161'
        )
    cipher = PKCS1_v1_5.new(priv)
    dsize = SHA.digest_size
    sentinel = Random.new().read(15 + dsize)

    # initial dict structure
    decrypted_data = {
        "customer": {
            "addresses": [],
            "documents": [],
            "scans": [],
        }
    }

    for customer_key in encrypted_data['customer'].keys():
        # iterate through lists with addresses, docs and scans
        if customer_key in ['addresses', 'documents', 'scans']:
            # iterate through internal keys of each list
            for i, inner in enumerate(encrypted_data['customer'][customer_key]):
                inner_dict = {}
                for inner_key in inner.keys():

                    # needn't decrypt Type and Scans's number (not Document's)
                    if inner_key in ['type', ]:
                        inner_dict[inner_key] = encrypted_data['customer'][customer_key][i][inner_key]
                    elif inner_key == 'number' and customer_key == 'scans':
                        inner_dict[inner_key] = encrypted_data['customer'][customer_key][i][inner_key]

                    # decrypt passport number
                    elif inner_key == 'number':
                        base64_decoded = base64.urlsafe_b64decode(
                            encrypted_data['customer'][customer_key][i][inner_key]
                        )
                        inner_dict[inner_key] = cipher.decrypt(
                            base64_decoded,
                            sentinel
                        ).decode('utf-8')

                    else:
                        base64_decoded = base64.urlsafe_b64decode(
                            encrypted_data['customer'][customer_key][i][inner_key]
                        )
                        # converting CamelCase keyname
                        # to camel_case keyname
                        new_key = "_".join(
                            [q.lower() for q in re.sub(r"([A-Z])", r" \1", inner_key).split()]
                        )
                        inner_dict[new_key] = cipher.decrypt(
                            base64_decoded,
                            sentinel
                        ).decode('utf-8')
                decrypted_data['customer'][customer_key].append(inner_dict)

        # don't convert Type and Signature values
        elif customer_key in ['type', 'signature']:
            decrypted_data['customer'][customer_key] = encrypted_data['customer'][customer_key]

        elif customer_key in ['clId', 'phone']:
            base64_decoded = base64.urlsafe_b64decode(
                encrypted_data['customer'][customer_key].encode().decode('utf-8')
            )
            # converting CamelCase keyname
            # to camel_case keyname
            new_key = "_".join(
                [q.lower() for q in re.sub(r"([A-Z])", r" \1", customer_key).split()]
            )
            decrypted_data['customer'][new_key] = cipher.decrypt(
                base64_decoded,
                sentinel
            ).decode('utf-8')
        else:
            base64_decoded = base64.urlsafe_b64decode(
                encrypted_data['customer'][customer_key]
            )
            # converting CamelCase keyname
            # to camel_case keyname
            new_key = "_".join(
                [q.lower() for q in re.sub(r"([A-Z])", r" \1", customer_key).split()]
            )
            decrypted_data['customer'][new_key] = cipher.decrypt(
                base64_decoded,
                sentinel
            ).decode('utf-8')
    # print("decrypted_data", decrypted_data)
    BankIDLog.objects.create(
        type='DecryptData',
        subtype="decrypted_data",
        message=decrypted_data
    )
    return decrypted_data


def load_scans(scans_list, headers):
    for scan in scans_list:
        response = requests.get(
            url=scan['link'],
            headers=headers,
            stream=True
        )
        save_to = '/home/phonxis/{0}.{1}'.format(
            scan['type'],
            scan['extension']
        )
        with open(save_to, 'wb') as f:
            f.write(response.content)


def local_save(decrypted_data, user, headers):
    documents = decrypted_data['customer']['documents']
    del decrypted_data['customer']['documents']
    addresses = decrypted_data['customer']['addresses']
    del decrypted_data['customer']['addresses']
    scans = decrypted_data['customer']['scans']
    del decrypted_data['customer']['scans']

    customer = Customer.objects.create(
        **decrypted_data['customer']
    )
    BankIDLog.objects.create(
        type='DecryptData',
        subtype="decrypted_data",
        message=decrypted_data
    )
    # Collect data for Questionnaire
    anketa_data = {
        'last_name': customer.last_name,
        'first_name': customer.first_name,
        'middle_name': customer.middle_name,
        'birthday_date': datetime.strptime(
            customer.birth_day,
            '%d.%m.%Y'
        ),
        'mobile_phone': customer.phone,
        'email': customer.email,
        'sex': 'male' if customer.sex == 'M' else 'female',
        'itn': customer.inn,
    }

    for doc in documents:
        doc_obj = Document.objects.create(
            customer=customer,
            **doc
        )
        # Save passport data to Questionnaire
        if doc_obj.type == 'passport':
            anketa_data.update({
                'passport_code': doc_obj.series + doc_obj.number,
                'passport_date': datetime.strptime(
                    doc_obj.date_issue,
                    '%d.%m.%Y'
                ) if doc_obj.date_issue else '9999-12-31',
                'passport_outdate': datetime.strptime(
                    doc_obj.date_expiration,
                    '%d.%m.%Y'
                ) if doc_obj.date_expiration else '9999-12-31',
                'passport_authority': doc_obj.issue
            })

    for address in addresses:
        addr_obj = Address.objects.create(
            customer=customer,
            **address
        )
        # Save factual address to Questionnaire's
        # residence and registration
        if addr_obj.type == 'factual':
            anketa_data.update({
                'residence_country': addr_obj.country,
                'residence_state': addr_obj.state,
                'residence_district': addr_obj.area,
                'residence_city': addr_obj.city,
                'residence_street': addr_obj.street,
                'residence_building': addr_obj.house_no,
                'residence_flat': addr_obj.flat_no,

                'registration_country': addr_obj.country,
                'registration_state': addr_obj.state,
                'registration_district': addr_obj.area,
                'registration_city': addr_obj.city,
                'registration_street': addr_obj.street,
                'registration_building': addr_obj.house_no,
                'registration_flat': addr_obj.flat_no,
            })

    for scan in scans:
        scan_obj = ScanDocument.objects.create(
            customer=customer,
            **scan
        )

        response = requests.get(
            url=scan['link'],
            headers=headers,
            stream=True
        )
        fp = BytesIO()
        fp.write(response.content)
        file_name = "{0}.{1}".format(
            scan['type'],
            scan['extension']
        )

        scan_obj.file.save(file_name, files.File(fp))
    # Save to Questionnaire model. Bound it with recent created user
    Questionnaire.objects.create(user=user, **anketa_data)
