from fastapi import APIRouter,File, UploadFile , Depends
from ...db.users import delete_user as del_user

router=APIRouter(prefix="/users", tags=["user-to-db"])
@router.post("/delete_user")
async def delete_user(user_id: int):
    del_user(user_id)
    return f" user_id {user_id} deleted from db successfully!"

