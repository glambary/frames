import ezdxf
from ezdxf import DXF2000
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace

from services.base.service import BaseService


class EzDxfService(BaseService):
    """Класс для работы с библиотекой ezdxf."""

    @staticmethod
    def get_document_and_model_space() -> tuple[Drawing, Modelspace]:
        """Возвращает dxf документ и модель."""
        document = ezdxf.new(dxfversion=DXF2000)
        model_space = document.modelspace()
        return document, model_space
