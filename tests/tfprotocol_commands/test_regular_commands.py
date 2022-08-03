# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from datetime import datetime
from time import sleep
from typing import List, Tuple

import pytest
from tfprotocol_client.misc.constants import KEY_LEN_INTERVAL
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import Date, TfProtocol

from .tfprotocol import tfprotocol_instance


@pytest.mark.run(order=35)
def test_echo_command(tfprotocol_instance: TfProtocol):
    """Test for echo command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    # ECHO command
    tfproto.echo_command('Hello World', response_handler=resps.append)
    assert resps[0] == 'Hello World'
