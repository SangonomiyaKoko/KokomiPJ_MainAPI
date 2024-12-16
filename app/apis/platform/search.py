# import gc

# from app.network import BasicAPI
# from app.log import ExceptionLogger
# from app.response import JSONResponse,  ResponseDict
# from app.utils import ShipName

# class Search:
#     @ExceptionLogger.handle_program_exception_async
#     async def search_ship(region_id: int, ship_name: str, language: str) -> ResponseDict:
#         try:
#             data = ShipName.search_ship(ship_name,region_id,language)
#             return JSONResponse.get_success_response(data)
#         except Exception as e:
#             raise e
#         finally:
#             gc.collect()

    