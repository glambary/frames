import ezdxf
from ezdxf import DXF2000
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace


class EzDxfService:
    @staticmethod
    def get_document_and_model_space() -> tuple[Drawing, Modelspace]:
        document = ezdxf.new(dxfversion=DXF2000)
        model_space = document.modelspace()
        return document, model_space
