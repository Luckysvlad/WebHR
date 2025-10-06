from openpyxl import Workbook

def make_template(path: str):
    wb = Workbook(); ws = wb.active; ws.title='Tasks'; ws.append(['department_code','position_name','function_name','task_name','weight','mandatory_for_level','mandatory_for_apex','is_active']); wb.save(path)
