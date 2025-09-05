import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.constants.date import DateFormats
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Cimb(BankBase):
    name = BankNames.CIMB

    # Credit statement configuration
    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        # Statement header contains two lines: "Post Date  Transaction Date  Description...  Transaction Amount (S$)"
        header_pattern=re.compile(r"Description\s+of\s+Transaction|Transaction\s+Amount", re.IGNORECASE),
        # Statement date line under SUMMARY OF ACCOUNTS: e.g. "04 Jul 2025"
        statement_date_pattern=re.compile(rf"\b({ISO8601.MMM_DD_YYYY}|{ISO8601.DD_MMM_YYYY})\b", re.IGNORECASE),
        prev_balance_pattern=StatementBalancePatterns.CIMB,
        transaction_pattern=CreditTransactionPatterns.CIMB,
        transaction_date_format="%d/%m",
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
    )

    # Debit statement configuration - based on actual CIMB statement format
    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        # Capture a month and year like "Aug 2025" anywhere on the page
        # Group(1) is required by BaseStatement._construct_date_string when named groups aren't provided
        statement_date_pattern=re.compile(
            rf"\b({DateFormats.MMM}\s+{DateFormats.YYYY})\b", re.IGNORECASE
        ),
        header_pattern=re.compile(
            r"(DATE.*TRANSACTION DETAILS.*WITHDRAWAL.*DEPOSIT.*BALANCE)"
        ),  # Actual CIMB header
        transaction_pattern=DebitTransactionPatterns.CIMB,
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            multiline_transaction_date=True,
            include_prev_margin=12,
            allow_no_date_no_amount_continuation=True,
            cimb_amount_first_balance_last=True,
            cimb_backfill_missing_date_from_last=True,
            cimb_allow_no_date_no_amount_continuation=True,
        ),
        transaction_bound=200,  # Increase boundary to accommodate CIMB layout
        transaction_date_format="%d %b",  # For "01 Aug" format
        safety_check=False,
    )

    # PDF configuration - adjust based on CIMB PDF characteristics
    pdf_config = PdfConfig(
        remove_vertical_text=False,  # Adjust based on CIMB PDF layout
    )

    # Bank identifiers for automatic detection
    identifiers = [
        [
            # You'll need to examine CIMB PDF metadata and text to set these
            TextIdentifier("CIMB"),  # Basic text identifier
            # MetadataIdentifier(creator="...", producer="..."),  # Add if known
        ],
    ]

    # Override statement_configs property
    statement_configs = [credit, debit]
