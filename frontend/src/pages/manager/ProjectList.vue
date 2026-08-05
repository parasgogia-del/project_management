<template>
  <div class="flex h-full flex-col">
    <!-- Page Header -->
    <PageHeader>
      <div class="flex items-center gap-2">
        <PageHeaderTitle title="Projects" />

        <span class="text-sm text-ink-gray-5">
          {{ filteredProjects.length }}
          {{ filteredProjects.length === 1 ? 'project' : 'projects' }}
        </span>
      </div>

      <Button
        route="/project/new"
        variant="solid"
        theme="blue"
        icon-left="plus"
      >
        New Project
      </Button>
    </PageHeader>

    <!-- Page Content -->
    <div class="w-full px-3 pb-10 pt-4 sm:px-5">
      <!-- Filters -->
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div class="flex w-full flex-wrap items-center gap-2 sm:w-auto">
          <!-- Search -->
          <TextInput
            v-model="searchQuery"
            type="text"
            placeholder="Search projects..."
            class="w-full sm:w-72"
          >
            <template #prefix>
              <span
                class="lucide-search size-4 text-ink-gray-5"
                aria-hidden="true"
              />
            </template>
          </TextInput>

          <!-- Status Filter -->
          <Select
            v-model="statusFilter"
            :options="projectStatusOptions"
            class="w-full sm:w-44"
          />
        </div>
      </div>

      <!-- Loading -->
      <div
        v-if="loading"
        class="flex min-h-[300px] items-center justify-center"
      >
        <LoadingIndicator class="h-6 w-6 text-ink-gray-4" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredProjects.length === 0"
        class="flex min-h-[360px] flex-col items-center justify-center rounded-lg border border-outline-gray-2 bg-surface-white px-4 text-center"
      >
        <div
          class="flex size-10 items-center justify-center rounded-full bg-surface-gray-2"
        >
          <span
            class="lucide-folder-open size-5 text-ink-gray-5"
            aria-hidden="true"
          />
        </div>

        <div class="mt-3 text-base font-medium text-ink-gray-8">
          No projects found
        </div>

        <p class="mt-1 max-w-sm text-p-sm text-ink-gray-5">
          Create your first project to get started.
        </p>

        <Button
          route="/project/new"
          variant="solid"
          theme="blue"
          icon-left="plus"
          class="mt-4"
        >
          New Project
        </Button>
      </div>

      <!-- Projects List -->
      <List
        v-else
        class="w-full list-row-px-3"
        :columns="[
          'minmax(0, 2fr)',
          '9rem',
          '10rem',
          '12rem',
        ]"
        :row-height="72"
      >
        <!-- Header -->
        <ListHeader>
          <ListHeaderCell>
            Project
          </ListHeaderCell>

          <ListHeaderCell>
            Status
          </ListHeaderCell>

          <ListHeaderCell>
            Progress
          </ListHeaderCell>

          <ListHeaderCell>
            Timeline
          </ListHeaderCell>
        </ListHeader>

        <!-- Rows -->
        <ListRows
          :items="filteredProjects"
          v-slot="{ item: project, value }"
        >
          <ListRow
            :value="value"
            :to="`/project/${project.name}`"
          >
            <!-- Project -->
            <ListCell>
              <div class="flex min-w-0 items-center gap-3">
                <!-- Folder Icon -->
                <div
                  class="flex size-9 shrink-0 items-center justify-center rounded-md bg-surface-gray-2"
                >
                  <span
                    class="lucide-folder size-4 text-ink-gray-5"
                    aria-hidden="true"
                  />
                </div>

                <!-- Project Information -->
                <div class="min-w-0">
                  <div
                    class="truncate text-base text-ink-gray-8"
                  >
                    {{ project.project_name }}
                  </div>

                  <div
                    v-if="project.client"
                    class="mt-0.5 truncate text-sm text-ink-gray-5"
                  >
                    {{ project.client }}
                  </div>

                  <div
                    v-if="project.description"
                    class="mt-0.5 truncate text-sm text-ink-gray-4"
                  >
                    {{ project.description }}
                  </div>
                </div>
              </div>
            </ListCell>

            <!-- Status -->
            <ListCell>
              <Badge
                :label="project.status"
                :theme="statusColorMap[project.status] || 'gray'"
              />
            </ListCell>

            <!-- Progress -->
            <ListCell>
              <div class="w-full max-w-[140px]">
                <div class="mb-1 flex items-center justify-between">
                  <span class="text-xs text-ink-gray-5">
                    Progress
                  </span>

                  <span class="text-xs font-medium text-ink-gray-7">
                    {{ project.progress || 0 }}%
                  </span>
                </div>

                <ProgressBar
                  :value="project.progress || 0"
                />
              </div>
            </ListCell>

            <!-- Timeline -->
            <ListCell>
              <div class="min-w-0">
                <!-- Dates -->
                <div
                  class="flex items-center gap-1.5 text-sm text-ink-gray-6"
                >
                  <span
                    class="lucide-calendar size-3.5 shrink-0 text-ink-gray-4"
                    aria-hidden="true"
                  />

                  <span v-if="project.start_date">
                    {{ formatDate(project.start_date) }}
                  </span>

                  <span
                    v-if="project.start_date && project.end_date"
                    class="text-ink-gray-3"
                  >
                    →
                  </span>

                  <span v-if="project.end_date">
                    {{ formatDate(project.end_date) }}
                  </span>

                  <span
                    v-if="!project.start_date && !project.end_date"
                    class="text-ink-gray-4"
                  >
                    No timeline
                  </span>
                </div>

                <!-- Project Manager -->
                <div
                  class="mt-1.5 flex min-w-0 items-center gap-1.5"
                >
                  <span
                    class="lucide-user size-3.5 shrink-0 text-ink-gray-4"
                    aria-hidden="true"
                  />

                  <span
                    class="truncate text-sm text-ink-gray-5"
                  >
                    {{ project.project_manager || 'Unassigned' }}
                  </span>
                </div>
              </div>
            </ListCell>
          </ListRow>
        </ListRows>
      </List>
    </div>
  </div>
</template>

<script>
import {
  Badge,
  Button,
  LoadingIndicator,
  PageHeader,
  PageHeaderTitle,
  Select,
  TextInput,
  frappeRequest,
} from 'frappe-ui'

import {
  List,
  ListCell,
  ListHeader,
  ListHeaderCell,
  ListRow,
  ListRows,
} from 'frappe-ui/list'

import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'ProjectList',

  components: {
    Badge,
    Button,
    LoadingIndicator,
    PageHeader,
    PageHeaderTitle,
    Select,
    TextInput,

    List,
    ListCell,
    ListHeader,
    ListHeaderCell,
    ListRow,
    ListRows,

    ProgressBar,
  },

  data() {
    return {
      projects: [],
      loading: true,
      searchQuery: '',
      statusFilter: '',

      projectStatusOptions: [
        { label: 'All Status', value: '' },
        { label: 'Planning', value: 'Planning' },
        { label: 'In Progress', value: 'In Progress' },
        { label: 'Completed', value: 'Completed' },
        { label: 'On Hold', value: 'On Hold' },
        { label: 'Cancelled', value: 'Cancelled' },
      ],
    }
  },

  computed: {
    filteredProjects() {
      return this.projects.filter((p) => {
        const search = this.searchQuery.toLowerCase()

        const matchSearch =
          !this.searchQuery ||
          p.project_name.toLowerCase().includes(search) ||
          (p.client || '').toLowerCase().includes(search)

        const matchStatus =
          !this.statusFilter ||
          p.status === this.statusFilter

        return matchSearch && matchStatus
      })
    },
  },

  mounted() {
    this.loadProjects()
  },

  methods: {
    async loadProjects() {
      this.loading = true

      try {
        const result = await frappeRequest({
          url: 'project_management.api.client.get_projects',
          method: 'POST',
        })

        this.projects = result || []
      } catch {
        this.projects = []
      } finally {
        this.loading = false
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return ''

      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      })
    },
  },
}
</script>
