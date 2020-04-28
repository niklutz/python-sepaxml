import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf():
    return SepaTransfer({
        "name": "Maria Bernasconi",
        "IBAN": "CH5109000000250092291",
        "batch": True,
        "currency": "CHF"
    }, schema="pain.001.001.03.ch.02")


# https://www.postfinance.ch/content/dam/pfch/doc/cust/download/musterfile/musterfile-pain.001.xml
SAMPLE_RESULT = b"""
<Document xmlns="http://www.six-interbank-clearing.com/de/pain.001.001.03.ch.02.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.six-interbank-clearing.com/de/pain.001.001.03.ch.02.xsd">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>20180724040432-d24ce3b3e284</MsgId>
      <CreDtTm>2018-07-24T16:04:32</CreDtTm>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>60.12</CtrlSum>
      <InitgPty>
        <Nm>Maria Bernasconi</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>MariaBernasconi-90102652f82a</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>60.12</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
      </PmtTpInf>
      <ReqdExctnDt>2018-07-24</ReqdExctnDt>
      <Dbtr>
        <Nm>Maria Bernasconi</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>CH5109000000250092291</IBAN>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId/>
      </DbtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>NOTPROVIDED</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="CHF">10.12</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId/>
        </CdtrAgt>
        <Cdtr>
          <Nm>Robert Schneider SA</Nm>
          <PstlAdr>
            <StrtNm>Rue du Lac 177</StrtNm>
            <PstCd>2503</PstCd>
            <TwnNm>Biel/Bienne</TwnNm>
            <Ctry>CH</Ctry>
          </PstlAdr>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>CH5109000000250092291</IBAN>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>Kontouebertrag</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>NOTPROVIDED</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="CHF">50.00</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId/>
        </CdtrAgt>
        <Cdtr>
          <Nm>Test du Test</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>CH5109000000250092291</IBAN>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>Test transaction2</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
"""


def test_two_debits(strf):
    payment1 = {
        "name": "Robert Schneider SA",
        "IBAN": "CH5109000000250092291",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Kontouebertrag",
        "address": {
          "street": "Rue du Lac 177",
          "postalcode": "2503",
          "city": "Biel/Bienne",
          "countrycode": "CH" # TODO: needs to be upper case, not verified
        }
    }
    payment2 = {
        "name": "Test du Test",
        "IBAN": "CH5109000000250092291",
        "amount": 5000,
        "execution_date": datetime.date.today(),
        "description": "Test transaction2"
    }

    strf.add_payment(payment1)
    strf.add_payment(payment2)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03.ch.02")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
