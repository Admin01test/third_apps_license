# -*- coding: utf-8 -*-
{
    'name': "Odoo Gantt View Project",

    'summary': """
        Gantt Native Exchange for Project,Project Gantt View,Project Gantt Native Web View,Gantt Native Report for Project,Web gantt view for projects,Gantt View for Project tasks,Gantt view for Project Issue,Gantt chart on the web,Gantt Native Web view
        """,

    'description': """
        odoo 14 project gantt view
        odoo 14 gantt view for project
        odoo 14 gantt chart
        odoo project gantt view
        gantt view in odoo
        project gantt view in odoo
    """,
    'author': "Ksolves India Ltd.",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 41.65,
    'live_test_url': 'https://ganttview14.kappso.com',
    'website': "https://store.ksolves.com",
    'maintainer': 'Ksolves India Ltd.',
    'category': 'Tools',
    'version': '14.1.1',
    'support': 'sales@ksolves.com',
    'depends': ['ks_gantt_view_base', 'project', 'hr', 'hr_timesheet', 'hr_holidays'],
    'images': [
        "static/description/blk_frd.jpg",
    ],
    'data': [
        'data/ks_task_due_alert.xml',
        'views/ks_gantt_task.xml',
        'views/ks_gantt_project_views.xml',
        'views/ks_project_task.xml',
        'views/ks_project_all_task.xml',
        'views/ks_gantt_view_project_assets.xml',
        'views/ks_gantt_import_wizard.xml',
        'reports/ks_tasks_report.xml',
        'reports/ks_timesheet_report.xml',
        'security/ir.model.access.csv',
    ],
}
