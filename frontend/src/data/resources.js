import { createResource } from 'frappe-ui'

// Project detail
export function useProject(name, portal = '') {
  return createResource({
    url: 'project_management.api.client.get_project',
    params: { name, portal },
    auto: false,
  })
}

// Deliverables
export function useDeliverables(project, portal = '') {
  return createResource({
    url: 'project_management.api.client.get_deliverables',
    params: { project, portal },
    auto: false,
  })
}

export function useDeliverablesWithDetails(project) {
  return createResource({
    url: 'project_management.api.client.get_deliverables_with_details',
    params: { project },
    auto: false,
  })
}

export function useDeliverable(name) {
  return createResource({
    url: 'project_management.api.client.get_deliverable',
    params: { name },
    auto: false,
  })
}

// Tasks
export function useTasks(filters = {}) {
  return createResource({
    url: 'project_management.api.client.get_tasks',
    params: filters,
    auto: false,
  })
}

export function useTask(name) {
  return createResource({
    url: 'project_management.api.client.get_task',
    params: { name },
    auto: false,
  })
}

// Time Logs
export function useTimeLogs(task) {
  return createResource({
    url: 'project_management.api.client.get_time_logs',
    params: { task },
    auto: false,
  })
}

// Comments
export function useComments(doctype, name) {
  return createResource({
    url: 'project_management.api.client.get_comments',
    params: { reference_doctype: doctype, reference_name: name },
    auto: false,
  })
}

// Files
export function useProjectFiles(project) {
  return createResource({
    url: 'project_management.api.file.get_project_files',
    params: { project },
    auto: false,
  })
}

export function useDeliverableFiles(deliverable) {
  return createResource({
    url: 'project_management.api.file.get_deliverable_files',
    params: { deliverable },
    auto: false,
  })
}

// Progress Report
export function useProgressReport(project, period) {
  return createResource({
    url: 'project_management.api.client.get_progress_report',
    params: { project, period },
    auto: false,
  })
}

// Gantt
export function useGanttTasks(project) {
  return createResource({
    url: 'project_management.api.client.get_gantt_tasks',
    params: { project },
    auto: false,
  })
}

// Notifications
export function useNotifications() {
  return createResource({
    url: 'project_management.api.client.get_notifications',
    auto: false,
  })
}

// Profile
export function useProfile() {
  return createResource({
    url: 'project_management.api.client.get_profile',
    auto: false,
  })
}

// Vendor APIs
export function useVendorProjects(vendor_name = '') {
  return createResource({
    url: 'project_management.api.vendor.get_vendor_projects',
    params: { vendor_name },
    auto: false,
  })
}

export function useVendorDeliverables(vendor_name = '') {
  return createResource({
    url: 'project_management.api.vendor.get_vendor_deliverables',
    params: { vendor_name },
    auto: false,
  })
}

export function useVendorTasks(vendor_name = '') {
  return createResource({
    url: 'project_management.api.vendor.get_vendor_tasks',
    params: { vendor_name },
    auto: false,
  })
}
