from typing import List, Tuple

import pytest
from tfprotocol_client.extensions.xs_ime import XSIme
from tfprotocol_client.misc.timeout_func import TimeLimitExpired, timelimit
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
import os
# pylint: disable=unused-import
from .xs_ime import (xsime_instance,XSIme)
from ..tfprotocol_commands.tfprotocol import tfprotocol_instance

@pytest.mark.ime
@pytest.mark.run(order=96)
def test_xsime_start_close_commands(
    
):
    """Test for open and close commands."""
    tfproto:XSIme = xsime_instance()
    resps: List[StatusInfo] = []
    # OPEN command
    try:
        timelimit(
            6,
            lambda *_, **__: tfproto.start_command(
                response_handler=resps.append
            ),
        )
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: open_command timeout'
        )
    index=0
    assert resps[index].status == StatusServerCode.OK, resps[index]
    
    
    try:
        timelimit(
            6,
            lambda *_, **__: tfproto.close_command(),
        )
        assert True, "close_command"
        
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: close_command timeout'
        )
    tfproto.disconnect()



@pytest.mark.ime
@pytest.mark.run(order=97)
@pytest.mark.parametrize("origin_user,destination_user"
                         ,[("user1","user2"),("user2","user1"),])
def test_xsime_send_messages_commands(
    origin_user,destination_user,
    
    tfprotocol_instance:tfprotocol_instance
    
):
    
    tfproto=xsime_instance()

    TIME_SEC_MAX=6
    tfproto:XSIme = tfproto
    resps: List[StatusInfo] = []
    # OPEN command
    try:
        timelimit(
            TIME_SEC_MAX,
            lambda *_, **__: tfproto.start_command(
                response_handler=resps.append
            ),
        )
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: open_command timeout'
        )
    index=0
    assert resps[index].status == StatusServerCode.OK, resps[index]


    NAME_CHAT="chattest"
    CHAT_FOLDER="/"+NAME_CHAT
    USER_1=origin_user
    USER_2=destination_user
    CHAT_FOLDER_USER_1="/"+NAME_CHAT+"/"+USER_1
    CHAT_FOLDER_USER_2="/"+NAME_CHAT+"/"+USER_2
    
    tfprotocol_instance.mkdir_command(CHAT_FOLDER)
    tfprotocol_instance.mkdir_command(CHAT_FOLDER_USER_1)
    tfprotocol_instance.mkdir_command(CHAT_FOLDER_USER_2)

    

    try:
        timelimit(
            10,
            lambda *_, **__: tfproto.setup_command(
            unique_user=True,auto_delete=False,timestamp=0
        ),
        )
        assert True, "setup_command"
        
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: setup_command timeout'
        )
    
    try:
        timelimit(
            TIME_SEC_MAX,
            lambda *_, **__: tfproto.set_path_command(path=CHAT_FOLDER),
        )
        assert True, "set_path_command"
        
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: set_path_command timeout'
        )

    try:
        timelimit(
            TIME_SEC_MAX,
            lambda *_, **__: tfproto.set_username_path_command(username_path=USER_1),
        )
        assert True, "set_username_path_command"
        
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: set_username_path_command timeout'
        )
    
    try:
        timelimit(
            TIME_SEC_MAX,
            lambda *_, **__: tfproto.send_message_command(message=f"mensaje de ${USER_1} a ${USER_2}",dest=USER_2),
        )
        assert True, "send_message_command"
        
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: send_message_command timeout'
        )
    
    
    try:
        timelimit(
            TIME_SEC_MAX,
            lambda *_, **__: tfproto.close_command(),
        )
        assert True, "close_command"
        
    except TimeLimitExpired:
        raise AssertionError(
            'Timeout expired: close_command timeout'
        )
    
    tfproto.disconnect()


#

    