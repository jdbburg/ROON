def calculate_total(price: float, quantity: int = 1, tax_rate: float = 0.1) -> float:
    """
    Calculate the total cost including tax.
    
    Args:
        price: Base price of the item
        quantity: Number of items
        tax_rate: Tax rate as a decimal
    """
    subtotal = price * quantity
    tax = subtotal * tax_rate
    return subtotal + tax

def get_coordinates(x: int, y: int) -> tuple[int, int]:
    """Returns a coordinate pair"""
    return (x, y)


import uproot
import json

from typing import TypedDict

# class RootFileResult(TypedDict):
#     file: uproot.ReadOnlyDirectory
#     keys: list[str]
#     view: str
    
# SetupUpRoot()
# def open_root_file(path: str = "example.root") -> RootFileResult:
#     """Facility for text visualization."""
#     f = uproot.open(path)
#     view = json.dumps(f.classnames(), indent=4)
#     return {
#         'file': f,
#         'keys': f.keys(),
#         'view': view,
#     }

def let( v ):
    return v

def print_pass( v, format_string=None ):
    try:
        if format_string and format_string != "" and format_string != "None":
            print(format_string % v)
        else:
            print(v)
    except Exception as e:
        print(e)

    return v
    
def bootrstrap( v, source:str = ""  ):
    exec(source)
    return v
