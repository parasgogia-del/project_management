<template>
  <div class="min-h-full bg-gray-50 p-6">
    <!-- =========================================================
         PAGE HEADER
    ========================================================== -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">
        Client Portal
      </h1>

      <p class="mt-1 text-sm text-gray-500">
        Overview of your projects
      </p>
    </div>

    <!-- =========================================================
         PROJECTS
    ========================================================== -->
    <div class="mb-8">
      <!-- Section Header -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-base font-semibold text-gray-900">
            My Projects
          </h2>

          <p class="mt-0.5 text-sm text-gray-500">
            Projects associated with your account
          </p>
        </div>

        <Badge
          :label="`${projects.length} Projects`"
          theme="gray"
        />
      </div>

      <!-- Project List -->
      <div
        v-if="projects.length"
        class="bg-white border border-gray-200 rounded-xl overflow-hidden"
      >
        <List
          class="w-full list-row-px-4"
          :columns="[
            'minmax(0, 2fr)',
            '8rem',
            '10rem',
            '7rem',
            '7rem'
          ]"
          :row-height="68"
        >
          <!-- Project List Header -->
          <ListHeader class="bg-gray-50">
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
              Start
            </ListHeaderCell>

            <ListHeaderCell>
              End
            </ListHeaderCell>
          </ListHeader>

          <!-- Project Rows -->
          <ListRows
            :items="visibleProjects"
            v-slot="{ item: project }"
          >
            <ListRow
              :value="project.name"
              class="cursor-pointer"
              @click="$router.push(`/client/project/${project.name}`)"
            >
              <!-- Project -->
              <ListCell>
                <div class="min-w-0 flex items-center gap-3">
                  <div
                    class="w-9 h-9 shrink-0 rounded-lg bg-blue-50 flex items-center justify-center"
                  >
                    <FeatherIcon
                      name="folder"
                      class="w-4 h-4 text-blue-600"
                    />
                  </div>

                  <div class="min-w-0">
                    <p
                      class="text-sm font-medium text-gray-900 truncate"
                      :title="project.project_name"
                    >
                      {{ project.project_name }}
                    </p>

                    <p class="text-xs text-gray-400 mt-0.5">
                      {{ project.name }}
                    </p>
                  </div>
                </div>
              </ListCell>

              <!-- Status -->
              <ListCell>
                <Badge
                  :label="project.status"
                  :theme="
                    statusColorMap[project.status] || 'gray'
                  "
                />
              </ListCell>

              <!-- Progress -->
              <ListCell>
                <div class="w-full max-w-[140px]">
                  <div
                    class="flex items-center justify-between mb-1.5"
                  >
                    <span class="text-xs text-gray-500">
                      Progress
                    </span>

                    <span class="text-xs font-medium text-gray-700">
                      {{ project.progress || 0 }}%
                    </span>
                  </div>

                  <div
                    class="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden"
                  >
                    <div
                      class="h-full bg-blue-500 rounded-full transition-all duration-300"
                      :style="{
                        width: `${project.progress || 0}%`,
                      }"
                    ></div>
                  </div>
                </div>
              </ListCell>

              <!-- Start Date -->
              <ListCell>
                <span class="text-sm text-gray-600">
                  {{ project.start_date || '—' }}
                </span>
              </ListCell>

              <!-- End Date -->
              <ListCell>
                <span class="text-sm text-gray-600">
                  {{ project.end_date || '—' }}
                </span>
              </ListCell>
            </ListRow>
          </ListRows>
        </List>

        <!-- Project Show More / Show Less -->
        <div
          v-if="projects.length > projectsPerPage"
          class="border-t border-gray-100 px-4 py-3 flex items-center justify-between bg-white"
        >
          <p class="text-xs text-gray-500">
            Showing
            {{ visibleProjects.length }}
            of
            {{ projects.length }}
            projects
          </p>

          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
            @click="toggleProjects"
          >
            {{ showAllProjects ? 'Show Less' : 'Show More' }}

            <FeatherIcon
              :name="
                showAllProjects
                  ? 'chevron-up'
                  : 'chevron-down'
              "
              class="w-4 h-4"
            />
          </button>
        </div>
      </div>

      <!-- Empty Projects -->
      <div
        v-else-if="!loading"
        class="bg-white border border-gray-200 rounded-xl"
      >
        <div
          class="flex flex-col items-center justify-center py-12 px-6 text-center"
        >
          <div
            class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-4"
          >
            <FeatherIcon
              name="folder"
              class="w-6 h-6 text-gray-400"
            />
          </div>

          <h3 class="text-sm font-semibold text-gray-800">
            No projects
          </h3>

          <p class="text-sm text-gray-500 mt-1">
            No projects found for your account
          </p>
        </div>
      </div>
    </div>

    <!-- =========================================================
         DELIVERABLES
    ========================================================== -->
    <div v-if="allDeliverables.length">
      <!-- Section Header -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-base font-semibold text-gray-900">
            All Deliverables
          </h2>

          <p class="mt-0.5 text-sm text-gray-500">
            Deliverables across all your projects
          </p>
        </div>

        <Badge
          :label="`${allDeliverables.length} Deliverables`"
          theme="gray"
        />
      </div>

      <!-- Deliverables List -->
      <div
        class="bg-white border border-gray-200 rounded-xl overflow-hidden"
      >
        <List
          class="w-full list-row-px-4"
          :columns="[
            'minmax(0, 2fr)',
            'minmax(0, 1fr)',
            '8rem',
            '9rem'
          ]"
          :row-height="64"
        >
          <!-- Deliverable List Header -->
          <ListHeader class="bg-gray-50">
            <ListHeaderCell>
              Deliverable
            </ListHeaderCell>

            <ListHeaderCell>
              Project
            </ListHeaderCell>

            <ListHeaderCell>
              Due Date
            </ListHeaderCell>

            <ListHeaderCell>
              Status
            </ListHeaderCell>
          </ListHeader>

          <!-- Deliverable Rows -->
          <ListRows
            :items="visibleDeliverables"
            v-slot="{ item: d }"
          >
            <ListRow
              :value="d.name"
              class="cursor-pointer"
              @click="$router.push(`/client/deliverable/${d.name}`)"
            >
              <!-- Deliverable -->
              <ListCell>
                <div class="flex items-center gap-3 min-w-0">
                  <div
                    class="w-8 h-8 shrink-0 rounded-lg bg-gray-100 flex items-center justify-center"
                  >
                    <FeatherIcon
                      name="file-text"
                      class="w-4 h-4 text-gray-500"
                    />
                  </div>

                  <div class="min-w-0">
                    <p
                      class="text-sm font-medium text-gray-800 truncate"
                      :title="d.title"
                    >
                      {{ d.title }}
                    </p>

                    <p class="text-xs text-gray-400 mt-0.5">
                      {{ d.name }}
                    </p>
                  </div>
                </div>
              </ListCell>

              <!-- Project -->
              <ListCell>
                <span
                  class="text-sm text-gray-600 truncate"
                  :title="d.project"
                >
                  {{ d.project }}
                </span>
              </ListCell>

              <!-- Due Date -->
              <ListCell>
                <span class="text-sm text-gray-600">
                  {{ d.due_date || '—' }}
                </span>
              </ListCell>

              <!-- Status -->
              <ListCell>
                <Badge
                  :label="d.status"
                  :theme="
                    statusColorMap[d.status] || 'gray'
                  "
                />
              </ListCell>
            </ListRow>
          </ListRows>
        </List>

        <!-- Deliverable Show More / Show Less -->
        <div
          v-if="allDeliverables.length > deliverablesPerPage"
          class="border-t border-gray-100 px-4 py-3 flex items-center justify-between bg-white"
        >
          <p class="text-xs text-gray-500">
            Showing
            {{ visibleDeliverables.length }}
            of
            {{ allDeliverables.length }}
            deliverables
          </p>

          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
            @click="toggleDeliverables"
          >
            {{ showAllDeliverables ? 'Show Less' : 'Show More' }}

            <FeatherIcon
              :name="
                showAllDeliverables
                  ? 'chevron-up'
                  : 'chevron-down'
              "
              class="w-4 h-4"
            />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  frappeRequest,
  Badge,
  FeatherIcon,
} from 'frappe-ui'

import {
  List,
  ListRow,
  ListCell,
  ListHeader,
  ListHeaderCell,
  ListRows,
} from 'frappe-ui/list'

import { statusColorMap } from '@/utils/statusColors'

export default {
  name: 'ClientDashboard',

  components: {
    Badge,
    FeatherIcon,
    List,
    ListRow,
    ListCell,
    ListHeader,
    ListHeaderCell,
    ListRows,
  },

  data() {
    return {
      projects: [],
      allDeliverables: [],
      loading: true,

      // UI-only controls
      projectsPerPage: 5,
      showAllProjects: false,

      deliverablesPerPage: 5,
      showAllDeliverables: false,
    }
  },

  computed: {
    // Show only first 5 projects initially
    visibleProjects() {
      if (this.showAllProjects) {
        return this.projects
      }

      return this.projects.slice(
        0,
        this.projectsPerPage
      )
    },

    // Show only first 5 deliverables initially
    visibleDeliverables() {
      if (this.showAllDeliverables) {
        return this.allDeliverables
      }

      return this.allDeliverables.slice(
        0,
        this.deliverablesPerPage
      )
    },
  },

  mounted() {
    this.loadAll()
    this.logSession()
  },

  methods: {
    async logSession() {
      try {
        const res = await frappeRequest({
          url: 'project_management.api.client.get_session_user',
          method: 'POST',
        })

        console.log(
          'Dashboard User:',
          res.user,
          '| Roles:',
          res.roles
        )
      } catch {}
    },

    async loadAll() {
      this.loading = true

      try {
        const pRes = await frappeRequest({
          url: 'project_management.api.client.get_my_projects',
          method: 'POST',
        })

        this.projects = pRes || []

        this.allDeliverables = []

        for (const project of this.projects) {
          this.allDeliverables.push(
            ...(project.deliverables || [])
          )
        }
      } catch {} finally {
        this.loading = false
      }
    },

    // UI-only toggle for projects
    toggleProjects() {
      this.showAllProjects = !this.showAllProjects
    },

    // UI-only toggle for deliverables
    toggleDeliverables() {
      this.showAllDeliverables =
        !this.showAllDeliverables
    },
  },
}
</script>
