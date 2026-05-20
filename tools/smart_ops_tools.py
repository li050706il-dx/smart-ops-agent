import json

from clients.smart_ops_api import (
    get_device_detail,
    search_devices,
    add_device,
    update_device,
    update_device_status,
    delete_device,

    create_workorder,
    get_workorder_detail,
    search_workorders,
    auto_assign_workorder,
    assign_workorder,
    accept_workorder,
    add_workorder_record,
    finish_workorder,
    evaluate_workorder,
    cancel_workorder,
    delete_workorder,

    create_inspection_plan,
    update_inspection_plan_status,
    search_inspection_plans,
    search_inspection_tasks,
    start_inspection_task,
    submit_inspection_task,

    get_unread_notice_count,
    search_notices,
    mark_notice_read,
    mark_all_notices_read,

    get_device_statistics,
    get_workorder_statistics,

    add_user,
    update_user_status,
    configure_worker_skills,
)

from rag.retriever import search_knowledge_base


def make_tool(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


tools = [
    # RAG
    make_tool(
        "search_knowledge_base",
        "检索智能运维工单管理系统的业务知识库。适用于查询系统角色、设备状态含义、工单流程、巡检流程、Redis、RabbitMQ、权限规则等规则类问题。",
        {
            "query": {"type": "string", "description": "要检索的业务规则或系统知识问题"}
        },
        ["query"]
    ),

    # 设备查询与操作
    make_tool(
        "get_device_detail",
        "根据设备ID查询设备详情。",
        {
            "device_id": {"type": "integer", "description": "设备ID"}
        },
        ["device_id"]
    ),
    make_tool(
        "search_devices",
        "分页查询设备。适用于查询某区域设备、某类型设备、故障设备、维修中设备、按名称或编号搜索设备。",
        {
            "page_no": {"type": "integer", "description": "页码，默认1"},
            "page_size": {"type": "integer", "description": "每页数量，默认10"},
            "device_no": {"type": "string", "description": "设备编号"},
            "device_name": {"type": "string", "description": "设备名称"},
            "device_type": {"type": "string", "description": "设备类型，例如空调、投影仪"},
            "area_code": {"type": "string", "description": "区域，例如A区"},
            "status": {"type": "integer", "description": "设备状态：1正常，2故障，3维修中，4停用"},
        }
    ),
    make_tool(
        "add_device",
        "新增设备。适用于管理员通过自然语言添加设备。",
        {
            "device_no": {"type": "string", "description": "设备编号"},
            "device_name": {"type": "string", "description": "设备名称"},
            "device_type": {"type": "string", "description": "设备类型"},
            "area_code": {"type": "string", "description": "区域编码"},
            "location": {"type": "string", "description": "具体位置"},
            "description": {"type": "string", "description": "设备描述"},
        },
        ["device_no", "device_name", "device_type", "area_code", "location"]
    ),
    make_tool(
        "update_device",
        "修改设备信息。适用于管理员修改设备名称、类型、区域、位置、描述等信息。",
        {
            "device_id": {"type": "integer", "description": "设备ID"},
            "device_no": {"type": "string", "description": "设备编号"},
            "device_name": {"type": "string", "description": "设备名称"},
            "device_type": {"type": "string", "description": "设备类型"},
            "area_code": {"type": "string", "description": "区域编码"},
            "location": {"type": "string", "description": "具体位置"},
            "description": {"type": "string", "description": "设备描述"},
        },
        ["device_id"]
    ),
    make_tool(
        "update_device_status",
        "修改设备状态。状态值：1正常，2故障，3维修中，4停用。",
        {
            "device_id": {"type": "integer", "description": "设备ID"},
            "status": {"type": "integer", "description": "设备状态：1正常，2故障，3维修中，4停用"},
        },
        ["device_id", "status"]
    ),
    make_tool(
        "delete_device",
        "删除设备。高风险操作，必须用户明确确认后才能执行。确认时 confirm=true。",
        {
            "device_id": {"type": "integer", "description": "设备ID"},
            "confirm": {"type": "boolean", "description": "用户是否已明确确认删除"},
        },
        ["device_id"]
    ),

    # 工单查询与操作
    make_tool(
        "create_workorder",
        "创建报修工单。适用于用户提交设备故障报修。",
        {
            "device_id": {"type": "integer", "description": "设备ID"},
            "title": {"type": "string", "description": "工单标题"},
            "description": {"type": "string", "description": "故障描述"},
            "fault_type": {"type": "string", "description": "故障类型"},
            "fault_location": {"type": "string", "description": "故障位置"},
            "contact_phone": {"type": "string", "description": "联系电话"},
            "priority": {"type": "integer", "description": "优先级，通常1-5"},
        },
        ["device_id", "title", "description", "fault_type", "fault_location", "contact_phone", "priority"]
    ),
    make_tool(
        "get_workorder_detail",
        "根据工单ID查询工单详情。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"}
        },
        ["workorder_id"]
    ),
    make_tool(
        "search_workorders",
        "分页查询工单。适用于查询待派单、处理中、已完成、某设备、某用户、某维修人员、某故障类型的工单。",
        {
            "page_no": {"type": "integer", "description": "页码，默认1"},
            "page_size": {"type": "integer", "description": "每页数量，默认10"},
            "status": {"type": "integer", "description": "工单状态"},
            "device_id": {"type": "integer", "description": "设备ID"},
            "user_id": {"type": "integer", "description": "报修用户ID"},
            "worker_id": {"type": "integer", "description": "维修人员ID"},
            "title": {"type": "string", "description": "工单标题关键词"},
            "fault_type": {"type": "string", "description": "故障类型"},
            "priority": {"type": "integer", "description": "优先级"},
        }
    ),
    make_tool(
        "auto_assign_workorder",
        "对指定工单执行系统自动派单。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"}
        },
        ["workorder_id"]
    ),
    make_tool(
        "assign_workorder",
        "管理员手动派单，将工单派给指定维修人员。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"},
            "worker_id": {"type": "integer", "description": "维修人员ID"},
        },
        ["workorder_id", "worker_id"]
    ),
    make_tool(
        "accept_workorder",
        "维修人员接单。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"}
        },
        ["workorder_id"]
    ),
    make_tool(
        "add_workorder_record",
        "给工单添加维修处理记录。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"},
            "content": {"type": "string", "description": "处理记录内容"},
        },
        ["workorder_id", "content"]
    ),
    make_tool(
        "finish_workorder",
        "完成工单。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"},
            "result": {"type": "string", "description": "维修完成结果说明"},
        },
        ["workorder_id", "result"]
    ),
    make_tool(
        "evaluate_workorder",
        "用户评价工单。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"},
            "score": {"type": "integer", "description": "评分"},
            "comment": {"type": "string", "description": "评价内容"},
        },
        ["workorder_id", "score"]
    ),
    make_tool(
        "cancel_workorder",
        "取消工单。重要操作，必须用户明确确认后才能执行。确认时 confirm=true。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"},
            "reason": {"type": "string", "description": "取消原因"},
            "confirm": {"type": "boolean", "description": "用户是否已明确确认取消"},
        },
        ["workorder_id", "reason"]
    ),
    make_tool(
        "delete_workorder",
        "删除工单。高风险操作，必须用户明确确认后才能执行。确认时 confirm=true。",
        {
            "workorder_id": {"type": "integer", "description": "工单ID"},
            "confirm": {"type": "boolean", "description": "用户是否已明确确认删除"},
        },
        ["workorder_id"]
    ),

    # 巡检操作
    make_tool(
        "create_inspection_plan",
        "创建巡检计划。",
        {
            "plan_name": {"type": "string", "description": "巡检计划名称"},
            "device_id": {"type": "integer", "description": "设备ID"},
            "inspector_id": {"type": "integer", "description": "巡检人员ID"},
            "cycle_type": {"type": "string", "description": "周期类型，例如DAILY、WEEKLY"},
            "description": {"type": "string", "description": "计划描述"},
        },
        ["plan_name", "device_id", "inspector_id", "cycle_type"]
    ),
    make_tool(
        "update_inspection_plan_status",
        "启用或停用巡检计划。",
        {
            "plan_id": {"type": "integer", "description": "巡检计划ID"},
            "status": {"type": "integer", "description": "状态值，具体以系统约定为准"},
        },
        ["plan_id", "status"]
    ),
    make_tool(
        "search_inspection_plans",
        "分页查询巡检计划。",
        {
            "page_no": {"type": "integer", "description": "页码"},
            "page_size": {"type": "integer", "description": "每页数量"},
            "plan_name": {"type": "string", "description": "计划名称"},
            "device_id": {"type": "integer", "description": "设备ID"},
            "inspector_id": {"type": "integer", "description": "巡检人员ID"},
            "status": {"type": "integer", "description": "巡检计划状态"},
        }
    ),
    make_tool(
        "search_inspection_tasks",
        "分页查询巡检任务。",
        {
            "page_no": {"type": "integer", "description": "页码"},
            "page_size": {"type": "integer", "description": "每页数量"},
            "plan_id": {"type": "integer", "description": "巡检计划ID"},
            "device_id": {"type": "integer", "description": "设备ID"},
            "inspector_id": {"type": "integer", "description": "巡检人员ID"},
            "status": {"type": "integer", "description": "任务状态"},
            "result": {"type": "string", "description": "巡检结果"},
        }
    ),
    make_tool(
        "start_inspection_task",
        "开始执行巡检任务。",
        {
            "task_id": {"type": "integer", "description": "巡检任务ID"}
        },
        ["task_id"]
    ),
    make_tool(
        "submit_inspection_task",
        "提交巡检任务结果。",
        {
            "task_id": {"type": "integer", "description": "巡检任务ID"},
            "result": {"type": "string", "description": "巡检结果，例如NORMAL或ABNORMAL"},
            "remark": {"type": "string", "description": "备注"},
        },
        ["task_id", "result"]
    ),

    # 通知操作
    make_tool(
        "get_unread_notice_count",
        "查询当前用户未读通知数量。",
        {}
    ),
    make_tool(
        "search_notices",
        "分页查询当前用户通知消息。",
        {
            "page_no": {"type": "integer", "description": "页码"},
            "page_size": {"type": "integer", "description": "每页数量"},
        }
    ),
    make_tool(
        "mark_notice_read",
        "将指定通知标记为已读。",
        {
            "notice_id": {"type": "integer", "description": "通知ID"}
        },
        ["notice_id"]
    ),
    make_tool(
        "mark_all_notices_read",
        "将当前用户所有通知标记为已读。批量操作，必须用户明确确认后才能执行。确认时 confirm=true。",
        {
            "confirm": {"type": "boolean", "description": "用户是否已明确确认全部已读"}
        }
    ),

    # 统计
    make_tool(
        "get_device_statistics",
        "查询设备统计数据。",
        {}
    ),
    make_tool(
        "get_workorder_statistics",
        "查询工单统计数据。",
        {}
    ),

    # 用户操作
    make_tool(
        "add_user",
        "新增用户。适用于管理员创建普通用户、维修人员、巡检人员或管理员账号。",
        {
            "username": {"type": "string", "description": "用户名"},
            "password": {"type": "string", "description": "初始密码"},
            "real_name": {"type": "string", "description": "真实姓名"},
            "role": {"type": "string", "description": "角色：ADMIN、USER、WORKER、INSPECTOR"},
            "phone": {"type": "string", "description": "手机号"},
        },
        ["username", "password", "real_name", "role"]
    ),
    make_tool(
        "update_user_status",
        "启用或禁用用户。权限相关操作，必须用户明确确认后才能执行。确认时 confirm=true。",
        {
            "user_id": {"type": "integer", "description": "用户ID"},
            "status": {"type": "integer", "description": "1启用，0禁用"},
            "confirm": {"type": "boolean", "description": "用户是否已明确确认"},
        },
        ["user_id", "status"]
    ),
    make_tool(
        "configure_worker_skills",
        "配置维修人员技能。",
        {
            "worker_id": {"type": "integer", "description": "维修人员ID"},
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "技能列表，例如空调维修、电路维修"
            },
        },
        ["worker_id", "skills"]
    ),
]


async def execute_tool(
    tool_name: str,
    arguments: str,
    token: str | None = None
) -> str:
    print("\n========== Agent Tool Call ==========")
    print(f"调用工具: {tool_name}")
    print(f"工具参数: {arguments}")

    try:
        args = json.loads(arguments or "{}")
    except Exception as e:
        result = {
            "error": f"工具参数 JSON 解析失败: {str(e)}",
            "raw_arguments": arguments
        }
        print(f"参数解析失败: {result}")
        print("=====================================\n")
        return json.dumps(result, ensure_ascii=False)

    tool_map = {
        # RAG
        "search_knowledge_base": search_knowledge_base,

        # 设备
        "get_device_detail": get_device_detail,
        "search_devices": search_devices,
        "add_device": add_device,
        "update_device": update_device,
        "update_device_status": update_device_status,
        "delete_device": delete_device,

        # 工单
        "create_workorder": create_workorder,
        "get_workorder_detail": get_workorder_detail,
        "search_workorders": search_workorders,
        "auto_assign_workorder": auto_assign_workorder,
        "assign_workorder": assign_workorder,
        "accept_workorder": accept_workorder,
        "add_workorder_record": add_workorder_record,
        "finish_workorder": finish_workorder,
        "evaluate_workorder": evaluate_workorder,
        "cancel_workorder": cancel_workorder,
        "delete_workorder": delete_workorder,

        # 巡检
        "create_inspection_plan": create_inspection_plan,
        "update_inspection_plan_status": update_inspection_plan_status,
        "search_inspection_plans": search_inspection_plans,
        "search_inspection_tasks": search_inspection_tasks,
        "start_inspection_task": start_inspection_task,
        "submit_inspection_task": submit_inspection_task,

        # 通知
        "get_unread_notice_count": get_unread_notice_count,
        "search_notices": search_notices,
        "mark_notice_read": mark_notice_read,
        "mark_all_notices_read": mark_all_notices_read,

        # 统计
        "get_device_statistics": get_device_statistics,
        "get_workorder_statistics": get_workorder_statistics,

        # 用户
        "add_user": add_user,
        "update_user_status": update_user_status,
        "configure_worker_skills": configure_worker_skills,
    }

    func = tool_map.get(tool_name)

    if func is None:
        result = {
            "error": f"未知工具：{tool_name}"
        }
        print(f"工具不存在: {result}")
        print("=====================================\n")
        return json.dumps(result, ensure_ascii=False)

    try:
        if tool_name == "search_knowledge_base":
            result = func(**args)
        else:
            result = await func(**args, token=token)

        print(f"工具执行成功，返回结果: {result}")
        print("=====================================\n")

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        result = {
            "error": str(e),
            "tool_name": tool_name,
            "arguments": args,
        }

        print(f"工具执行失败: {result}")
        print("=====================================\n")

        return json.dumps(result, ensure_ascii=False)