from email.message import Message
import json

import apmodel
from typing import Union
from apmodel.types import ActivityPubModel
import charset_normalizer as chardet
from typing import Any, Callable
from typing_extensions import Optional
import httpcore

from .exceptions import ContentTypeError
from .._common import _is_expected_content_type

JSONDecoder = Callable[[str], Any]
DEFAULT_JSON_DECODER = json.loads

class Response:
    def __init__(self, response: httpcore.Response) -> None:
        self.__response = response

    def _get_encoding_from_header(self) -> Optional[str]:
        ctype_value = self.headers.get("Content-Type")
        
        if not ctype_value:
            return None
        
        try:
            msg = Message()
            msg['Content-Type'] = ctype_value 
            
            charset = msg.get_param('charset')
            
            if isinstance(charset, str):
                return charset.lower()
            
            return None
                
        except Exception:
            return None
            
    @property
    def ok(self) -> bool:
        return self.status >= 200 and self.status <= 299
        
    @property
    def status(self) -> int:
        return self.__response.status
        
    @property
    def body(self) -> bytes:
        return self.__response.content
        
    @property
    def headers(self) -> dict[str, str]:
        return {
            key.decode('utf-8'): value.decode('utf-8') 
            for key, value in self.__response.headers
        }

    def json(
        self,
        *,
        encoding: Optional[str] = None,
        loads: Callable[[str], Any] = DEFAULT_JSON_DECODER,
        content_type: Optional[str] = "application/json",
    ) -> Any:
        """Read and decodes JSON response."""
        if content_type:
            ctype = self.headers.get("Content-Type", "").lower() 
            
            if not _is_expected_content_type(ctype, content_type):
                raise ContentTypeError(
                    message=(
                        "Attempt to decode JSON with unexpected mimetype: %s" % ctype
                    ),
                    status=self.status,
                    headers=self.headers,
                )

        if self.body is None:
             return None

        stripped = self.body.strip()
        if not stripped:
            return None

        if encoding is None:
            header_encoding = self._get_encoding_from_header()
            
            if header_encoding:
                encoding = header_encoding
            else:
                best_match = chardet.from_bytes(stripped).best()
                if best_match:
                    encoding = best_match.encoding
                else:
                    encoding = 'utf-8'

        return loads(stripped.decode(encoding))

    def parse(
        self,
        *,
        encoding: Optional[str] = None,
        loads: JSONDecoder = DEFAULT_JSON_DECODER,
    ) -> Union[ActivityPubModel, dict]:
        json = self.json(
            encoding=encoding,
            loads=loads
        )
        return apmodel.load(json)