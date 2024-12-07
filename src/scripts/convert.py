import logging
from pathlib import Path

import ezdxf
from ezdxf import DXF2000


def convert_dxf_to_2000(input_folder: str) -> None:
    """
    Конвертирует файлы.

    DXF файлы в папке input_folder в формат DXF 2000 и сохраняет в новую папку
    с постфиксом "_2000".

    :param input_folder: Путь к исходной папке с DXF файлами.
    """
    input_path = Path(input_folder).resolve()
    output_path = input_path.parent / f"{input_path.name}_2000"
    output_path.mkdir(exist_ok=True)

    for dxf_file in input_path.glob("*.dxf"):
        try:
            doc = ezdxf.readfile(dxf_file)

            doc.dxfversion = DXF2000
            output_file = output_path / dxf_file.name
            doc.saveas(output_file)
            logging.info(f"Файл {dxf_file.name} успешно конвертирован.")
        except ezdxf.DXFStructureError:
            logging.info(
                f"Ошибка чтения DXF файла: {dxf_file.name}. Пропускаем."
            )
        except Exception as e:
            logging.info(f"Не удалось обработать файл {dxf_file.name}: {e}")


if __name__ == "__main__":
    # Укажите путь к папке с исходными DXF файлами
    folder_path = input("Введите путь к папке с DXF файлами: ").strip()
    if Path.isdir(folder_path):  # noqa: PTH112
        convert_dxf_to_2000(folder_path)
    else:
        logging.info("Указанная папка не найдена. Проверьте путь.")
