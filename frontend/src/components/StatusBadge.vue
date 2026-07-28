<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="colorClasses"
  >
    {{ label || status }}
  </span>
</template>

<script>
const STATUS_COLORS = {
  // Project statuses
  'Planning': 'bg-gray-100 text-gray-700',
  'In Progress': 'bg-blue-100 text-blue-700',
  'Completed': 'bg-green-100 text-green-700',
  'On Hold': 'bg-yellow-100 text-yellow-700',
  'Cancelled': 'bg-red-100 text-red-700',
  // Task statuses
  'Open': 'bg-gray-100 text-gray-700',
  'Working': 'bg-blue-100 text-blue-700',
  'Blocked': 'bg-red-100 text-red-700',
  // Deliverable statuses
  'Draft': 'bg-gray-100 text-gray-700',
  'WIP': 'bg-blue-100 text-blue-700',
  'Ready for Approval': 'bg-indigo-100 text-indigo-700',
  'Awaiting Client Review': 'bg-purple-100 text-purple-700',
  'Approved': 'bg-green-100 text-green-700',
  'Changes Requested': 'bg-orange-100 text-orange-700',
  // Priority
  'Low': 'bg-gray-100 text-gray-600',
  'Medium': 'bg-blue-100 text-blue-700',
  'High': 'bg-orange-100 text-orange-700',
  'Critical': 'bg-red-100 text-red-700',
  // Vendor statuses
  'Active': 'bg-green-100 text-green-700',
  'Inactive': 'bg-gray-100 text-gray-600',
  'Suspended': 'bg-red-100 text-red-700',
}

export default {
  name: 'StatusBadge',
  props: {
    status: { type: String, default: '' },
    label: { type: String, default: '' },
    color: { type: String, default: '' },
  },
  computed: {
    colorClasses() {
      if (this.color) return this.color
      return STATUS_COLORS[this.status] || 'bg-gray-100 text-gray-600'
    },
  },
}
</script>
