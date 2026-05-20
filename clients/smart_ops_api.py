import httpx

from config import SMART_OPS_BASE_URL


def build_headers(token: str | None = None) -> dict:
    headers = {
        "Content-Type": "application/json"
    }

    if token:
        headers["Authorization"] = token

    return headers


async def request_java_api(
    method: str,
    path: str,
    token: str | None = None,
    params: dict | None = None,
    json: dict | None = None,
) -> dict:
    url = f"{SMART_OPS_BASE_URL}{path}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=build_headers(token),
            params=params,
            json=json,
        )

    try:
        return response.json()
    except Exception:
        return {
            "success": False,
            "http_status": response.status_code,
            "error": response.text,
        }


# =========================
# 设备模块
# =========================

async def get_device_detail(device_id: int, token: str | None = None) -> dict:
    return await request_java_api(
        method="GET",
        path=f"/devices/{device_id}",
        token=token,
    )


async def search_devices(
    page_no: int = 1,
    page_size: int = 10,
    device_no: str | None = None,
    device_name: str | None = None,
    device_type: str | None = None,
    area_code: str | None = None,
    status: int | None = None,
    token: str | None = None,
) -> dict:
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
    }

    if device_no:
        params["deviceNo"] = device_no
    if device_name:
        params["deviceName"] = device_name
    if device_type:
        params["deviceType"] = device_type
    if area_code:
        params["areaCode"] = area_code
    if status is not None:
        params["status"] = status

    return await request_java_api(
        method="GET",
        path="/devices/page",
        token=token,
        params=params,
    )


async def add_device(
    device_no: str,
    device_name: str,
    device_type: str,
    area_code: str,
    location: str,
    description: str | None = None,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path="/devices",
        token=token,
        json={
            "deviceNo": device_no,
            "deviceName": device_name,
            "deviceType": device_type,
            "areaCode": area_code,
            "location": location,
            "description": description,
        },
    )


async def update_device(
    device_id: int,
    device_no: str | None = None,
    device_name: str | None = None,
    device_type: str | None = None,
    area_code: str | None = None,
    location: str | None = None,
    description: str | None = None,
    token: str | None = None,
) -> dict:
    body = {
        "id": device_id,
        "deviceNo": device_no,
        "deviceName": device_name,
        "deviceType": device_type,
        "areaCode": area_code,
        "location": location,
        "description": description,
    }

    body = {k: v for k, v in body.items() if v is not None}

    return await request_java_api(
        method="PUT",
        path="/devices",
        token=token,
        json=body,
    )


async def update_device_status(
    device_id: int,
    status: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="PUT",
        path=f"/devices/{device_id}/status",
        token=token,
        json={"status": status},
    )


async def delete_device(
    device_id: int,
    confirm: bool = False,
    token: str | None = None,
) -> dict:
    if not confirm:
        return {
            "need_confirm": True,
            "message": f"删除设备 {device_id} 属于高风险操作。请用户明确回复：确认删除设备{device_id}。"
        }

    return await request_java_api(
        method="DELETE",
        path=f"/devices/{device_id}",
        token=token,
    )


# =========================
# 工单模块
# =========================

async def create_workorder(
    device_id: int,
    title: str,
    description: str,
    fault_type: str,
    fault_location: str,
    contact_phone: str,
    priority: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path="/workorders",
        token=token,
        json={
            "deviceId": device_id,
            "title": title,
            "description": description,
            "faultType": fault_type,
            "faultLocation": fault_location,
            "contactPhone": contact_phone,
            "priority": priority,
        },
    )


async def get_workorder_detail(
    workorder_id: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="GET",
        path=f"/workorders/{workorder_id}/detail",
        token=token,
    )


async def search_workorders(
    page_no: int = 1,
    page_size: int = 10,
    status: int | None = None,
    device_id: int | None = None,
    user_id: int | None = None,
    worker_id: int | None = None,
    title: str | None = None,
    fault_type: str | None = None,
    priority: int | None = None,
    token: str | None = None,
) -> dict:
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
    }

    if status is not None:
        params["status"] = status
    if device_id is not None:
        params["deviceId"] = device_id
    if user_id is not None:
        params["userId"] = user_id
    if worker_id is not None:
        params["workerId"] = worker_id
    if title:
        params["title"] = title
    if fault_type:
        params["faultType"] = fault_type
    if priority is not None:
        params["priority"] = priority

    return await request_java_api(
        method="GET",
        path="/workorders/page",
        token=token,
        params=params,
    )


async def auto_assign_workorder(
    workorder_id: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/auto-assign",
        token=token,
        json={},
    )


async def assign_workorder(
    workorder_id: int,
    worker_id: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/assign",
        token=token,
        json={"workerId": worker_id},
    )


async def accept_workorder(
    workorder_id: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/accept",
        token=token,
        json={},
    )


async def add_workorder_record(
    workorder_id: int,
    content: str,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/records",
        token=token,
        json={"content": content},
    )


async def finish_workorder(
    workorder_id: int,
    result: str,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/finish",
        token=token,
        json={"result": result},
    )


async def evaluate_workorder(
    workorder_id: int,
    score: int,
    comment: str | None = None,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/evaluate",
        token=token,
        json={
            "score": score,
            "comment": comment,
        },
    )


async def cancel_workorder(
    workorder_id: int,
    reason: str,
    confirm: bool = False,
    token: str | None = None,
) -> dict:
    if not confirm:
        return {
            "need_confirm": True,
            "message": f"取消工单 {workorder_id} 属于重要操作。请用户明确回复：确认取消工单{workorder_id}。"
        }

    return await request_java_api(
        method="POST",
        path=f"/workorders/{workorder_id}/cancel",
        token=token,
        json={"reason": reason},
    )


async def delete_workorder(
    workorder_id: int,
    confirm: bool = False,
    token: str | None = None,
) -> dict:
    if not confirm:
        return {
            "need_confirm": True,
            "message": f"删除工单 {workorder_id} 属于高风险操作。请用户明确回复：确认删除工单{workorder_id}。"
        }

    return await request_java_api(
        method="DELETE",
        path=f"/workorders/{workorder_id}",
        token=token,
    )


# =========================
# 巡检模块
# =========================

async def create_inspection_plan(
    plan_name: str,
    device_id: int,
    inspector_id: int,
    cycle_type: str,
    description: str | None = None,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path="/inspection/plans",
        token=token,
        json={
            "planName": plan_name,
            "deviceId": device_id,
            "inspectorId": inspector_id,
            "cycleType": cycle_type,
            "description": description,
        },
    )


async def update_inspection_plan_status(
    plan_id: int,
    status: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="PUT",
        path=f"/inspection/plans/{plan_id}/status",
        token=token,
        json={"status": status},
    )


async def search_inspection_plans(
    page_no: int = 1,
    page_size: int = 10,
    plan_name: str | None = None,
    device_id: int | None = None,
    inspector_id: int | None = None,
    status: int | None = None,
    token: str | None = None,
) -> dict:
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
    }

    if plan_name:
        params["planName"] = plan_name
    if device_id is not None:
        params["deviceId"] = device_id
    if inspector_id is not None:
        params["inspectorId"] = inspector_id
    if status is not None:
        params["status"] = status

    return await request_java_api(
        method="GET",
        path="/inspection/plans/page",
        token=token,
        params=params,
    )


async def search_inspection_tasks(
    page_no: int = 1,
    page_size: int = 10,
    plan_id: int | None = None,
    device_id: int | None = None,
    inspector_id: int | None = None,
    status: int | None = None,
    result: str | None = None,
    token: str | None = None,
) -> dict:
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
    }

    if plan_id is not None:
        params["planId"] = plan_id
    if device_id is not None:
        params["deviceId"] = device_id
    if inspector_id is not None:
        params["inspectorId"] = inspector_id
    if status is not None:
        params["status"] = status
    if result:
        params["result"] = result

    return await request_java_api(
        method="GET",
        path="/inspection/tasks/page",
        token=token,
        params=params,
    )


async def start_inspection_task(
    task_id: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/inspection/tasks/{task_id}/start",
        token=token,
        json={},
    )


async def submit_inspection_task(
    task_id: int,
    result: str,
    remark: str | None = None,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/inspection/tasks/{task_id}/submit",
        token=token,
        json={
            "result": result,
            "remark": remark,
        },
    )


# =========================
# 通知模块
# =========================

async def get_unread_notice_count(
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="GET",
        path="/notices/unread/count",
        token=token,
    )


async def search_notices(
    page_no: int = 1,
    page_size: int = 10,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="GET",
        path="/notices/page",
        token=token,
        params={
            "pageNo": page_no,
            "pageSize": page_size,
        },
    )


async def mark_notice_read(
    notice_id: int,
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="PUT",
        path=f"/notices/{notice_id}/read",
        token=token,
        json={},
    )


async def mark_all_notices_read(
    confirm: bool = False,
    token: str | None = None,
) -> dict:
    if not confirm:
        return {
            "need_confirm": True,
            "message": "全部通知标记为已读属于批量操作。请用户明确回复：确认全部通知已读。"
        }

    return await request_java_api(
        method="PUT",
        path="/notices/read/all",
        token=token,
        json={},
    )


# =========================
# 统计模块
# =========================

async def get_device_statistics(
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="GET",
        path="/statistics/devices",
        token=token,
    )


async def get_workorder_statistics(
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="GET",
        path="/statistics/workorders",
        token=token,
    )


# =========================
# 用户模块
# =========================

async def add_user(
    username: str,
    password: str,
    real_name: str,
    role: str,
    phone: str | None = None,
    token: str | None = None,
) -> dict:
    body = {
        "username": username,
        "password": password,
        "realName": real_name,
        "role": role,
        "phone": phone,
    }

    body = {k: v for k, v in body.items() if v is not None}

    return await request_java_api(
        method="POST",
        path="/users",
        token=token,
        json=body,
    )


async def update_user_status(
    user_id: int,
    status: int,
    confirm: bool = False,
    token: str | None = None,
) -> dict:
    if not confirm:
        action = "启用" if status == 1 else "禁用"
        return {
            "need_confirm": True,
            "message": f"{action}用户 {user_id} 属于权限相关操作。请用户明确回复：确认{action}用户{user_id}。"
        }

    return await request_java_api(
        method="PUT",
        path=f"/users/{user_id}/status",
        token=token,
        json={"status": status},
    )


async def configure_worker_skills(
    worker_id: int,
    skills: list[str],
    token: str | None = None,
) -> dict:
    return await request_java_api(
        method="POST",
        path=f"/users/workers/{worker_id}/skills",
        token=token,
        json={"skills": skills},
    )