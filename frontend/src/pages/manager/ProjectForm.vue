<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ isEdit ? 'Edit Project' : 'Create Project' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">{{ isEdit ? 'Update project details' : 'Set up a new project' }}</p>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <div class="space-y-5">
        <Input
          v-model="form.project_name"
          label="Project Name *"
          placeholder="Enter project name"
        />

        <div class="grid grid-cols-2 gap-4">
          <Autocomplete
            :model-value="form.client"
            :options="formOptions.clients"
            label="Client *"
            placeholder="Search or select a client"
            @change="form.client = $event?.value || ''"
          />
          <Autocomplete
            :model-value="form.project_manager"
            :options="formOptions.project_managers"
            label="Project Manager"
            placeholder="Search or select a manager"
            @change="form.project_manager = $event?.value || ''"
          />
        </div>

        <Input
          type="select"
          v-model="form.status"
          label="Status"
          :options="projectStatusOptions"
        />

        <div class="grid grid-cols-2 gap-4">
          <Input
            type="date"
            v-model="form.start_date"
            label="Start Date"
          />
          <Input
            type="date"
            v-model="form.end_date"
            label="End Date"
          />
        </div>

        <Input
          type="textarea"
          v-model="form.description"
          label="Description"
          :rows="3"
          placeholder="Project description..."
        />
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <h2 class="text-sm font-semibold text-gray-800 mb-4">Billing (ERPNext)</h2>
      <p v-if="billingError" class="text-xs text-red-500 mb-3">{{ billingError }}</p>
      <div class="grid grid-cols-2 gap-4">
        <Autocomplete
          :model-value="form.customer"
          :options="billingOptions.customers"
          label="Customer"
          placeholder="Select ERPNext customer"
          @change="form.customer = $event?.value || ''"
        />
        <Autocomplete
          :model-value="form.billing_company"
          :options="billingOptions.companies"
          label="Company"
          placeholder="Select company"
          @change="form.billing_company = $event?.value || ''"
        />
        <Autocomplete
          :model-value="form.billing_currency"
          :options="billingOptions.currencies"
          label="Currency"
          placeholder="Select currency"
          @change="form.billing_currency = $event?.value || ''"
        />
      </div>
      <p class="text-xs text-gray-400 mt-3">
        Set a Customer and Company to enable generating Sales Invoices for approved deliverables.
      </p>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-gray-800">Project Members</h2>
        <Button variant="ghost" icon-left="plus" @click="addMember">Add Member</Button>
      </div>
      <div v-if="form.project_members.length === 0" class="text-xs text-gray-400 text-center py-4">
        No members added
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="(member, idx) in form.project_members"
          :key="idx"
          class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
        >
          <Autocomplete
            :model-value="member.user"
            :options="formOptions.members"
            placeholder="Search or select a member"
            class="flex-1"
            @change="member.user = $event?.value || ''"
          />
          <Input
            type="select"
            v-model="member.project_role"
            :options="memberRoleOptions"
            class="w-44 shrink-0"
          />
          <Input
            type="checkbox"
            v-model="member.is_active"
            label="Active"
            class="shrink-0"
          />
          <Button variant="ghost" icon="x" @click="removeMember(idx)" class="shrink-0" />
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-gray-800">Vendors</h2>
        <Button variant="ghost" icon-left="plus" @click="addVendor">Add Vendor</Button>
      </div>
      <div v-if="form.vendors.length === 0" class="text-xs text-gray-400 text-center py-4">
        No vendors added
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="(vendor, idx) in form.vendors"
          :key="idx"
          class="p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <Autocomplete
              :model-value="vendor.vendor"
              :options="formOptions.vendors"
              placeholder="Search or select a vendor"
              class="flex-1"
              @change="vendor.vendor = $event?.value || ''"
            />
            <Input
              type="select"
              v-model="vendor.status"
              :options="vendorStatusOptions"
              class="w-36 shrink-0"
            />
            <Button variant="ghost" icon="x" @click="removeVendor(idx)" class="shrink-0" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
            <Autocomplete
              :model-value="vendor.supplier"
              :options="billingOptions.suppliers"
              placeholder="Supplier (ERPNext)"
              class="w-full"
              @change="vendor.supplier = $event?.value || ''"
            />
            <Autocomplete
              :model-value="vendor.item"
              :options="billingOptions.items"
              placeholder="Item"
              class="w-full"
              @change="vendor.item = $event?.value || ''"
            />
            <Input
              v-model="vendor.amount"
              type="number"
              placeholder="Purchase amount"
              class="w-full"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-end gap-3">
      <Button variant="outline" @click="$router.back()">Cancel</Button>
      <Button
        theme="blue" variant="solid"
        :disabled="!form.project_name || !form.client"
        :loading="saving"
        :loading-text="saving ? 'Saving...' : null"
        @click="saveProject"
      >{{ isEdit ? 'Update Project' : 'Create Project' }}</Button>
    </div>

    <p v-if="error" class="text-xs text-red-500 text-center">{{ error }}</p>
  </div>
</template>

<script>
import { frappeRequest, Button, Input, Autocomplete } from 'frappe-ui'
import { useProject } from '@/data/resources'

export default {
  name: 'ProjectForm',
  components: { Button, Input, Autocomplete },
  data() {
    return {
      isEdit: false,
      saving: false,
      error: '',
      formOptions: { clients: [], project_managers: [], members: [], vendors: [] },
      billingOptions: { customers: [], companies: [], currencies: [], items: [], suppliers: [] },
      billingError: '',
      projectStatusOptions: ['Planning', 'In Progress', 'Completed', 'On Hold', 'Cancelled'],
      memberRoleOptions: ['Project Manager', 'Developer', 'Designer', 'QA', 'Business Analyst', 'UI/UX Designer', 'Client Reviewer'],
      vendorStatusOptions: ['Active', 'Inactive', 'Suspended'],
      form: {
        project_name: '',
        client: '',
        project_manager: '',
        status: 'Planning',
        start_date: '',
        end_date: '',
        description: '',
        customer: '',
        billing_company: '',
        billing_currency: '',
        project_members: [],
        vendors: [],
      },
    }
  },
  mounted() {
    this.loadFormOptions()
    if (this.$route.params.id) {
      this.isEdit = true
      this.loadProject(this.$route.params.id)
    }
  },
  methods: {
    async     loadFormOptions() {
      try {
        const res = await frappeRequest({
          url: 'project_management.api.client.get_form_options',
          method: 'POST',
        })
        this.formOptions = res || this.formOptions
      } catch {}
      try {
        const billing = await frappeRequest({
          url: 'project_management.api.invoicing.get_billing_config',
          method: 'POST',
        })
        this.billingOptions = {
          customers: (billing.customers || []).map(c => ({
            label: c.customer_name || c.name,
            value: c.name,
          })),
          companies: billing.companies || [],
          currencies: billing.currencies || [],
        }
      } catch (err) {
        this.billingError = err.message || 'ERPNext integration not available'
      }
      try {
        const purchasing = await frappeRequest({
          url: 'project_management.api.purchasing.get_purchase_config',
          method: 'POST',
        })
        if (purchasing) {
          this.billingOptions.items = purchasing.items || this.billingOptions.items
          this.billingOptions.suppliers = purchasing.suppliers || this.billingOptions.suppliers
        }
      } catch {}
    },
    async loadProject(name) {
      try {
        const project = await useProject(name).fetch()
        if (project) {
          this.form = {
            project_name: project.project_name,
            client: project.client,
            project_manager: project.project_manager || '',
            status: project.status || 'Planning',
            start_date: project.start_date || '',
            end_date: project.end_date || '',
            description: project.description || '',
            customer: project.customer || '',
            billing_company: project.billing_company || '',
            billing_currency: project.billing_currency || '',
            project_members: (project.project_members || []).map(m => ({
              name: m.name,
              user: m.user,
              project_role: m.project_role,
              is_active: m.is_active,
              assigned_on: m.assigned_on,
              notes: m.notes || '',
            })),
            vendors: (project.vendors || []).map(v => ({
              name: v.name,
              vendor: v.vendor,
              supplier: v.supplier || '',
              status: v.status || 'Active',
              item: v.item || '',
              amount: v.amount || 0,
              is_billed: v.is_billed || 0,
              purchase_invoice: v.purchase_invoice || null,
              contract_start: v.contract_start,
              contract_end: v.contract_end,
              notes: v.notes || '',
            })),
          }
        }
      } catch (err) {
        this.error = 'Failed to load project'
      }
    },
    addMember() {
      this.form.project_members.push({
        user: '',
        project_role: 'Developer',
        is_active: 1,
        assigned_on: new Date().toISOString().split('T')[0],
        notes: '',
      })
    },
    removeMember(idx) {
      this.form.project_members.splice(idx, 1)
    },
    addVendor() {
      this.form.vendors.push({
        vendor: '',
        supplier: '',
        status: 'Active',
        item: '',
        amount: 0,
        is_billed: 0,
        purchase_invoice: null,
        notes: '',
      })
    },
    removeVendor(idx) {
      this.form.vendors.splice(idx, 1)
    },
    async saveProject() {
      this.saving = true
      this.error = ''

      const memberEmails = this.form.project_members.map(m => m.user).filter(Boolean)
      const uniqueEmails = new Set(memberEmails)
      if (memberEmails.length !== uniqueEmails.size) {
        this.error = 'Duplicate team members found. Please remove duplicates before saving.'
        this.saving = false
        return
      }

      try {
        if (this.isEdit) {
          await frappeRequest({
            url: 'project_management.api.client.update_project',
            method: 'POST',
            params: { name: this.$route.params.id, data: this.form },
          })
        } else {
          await frappeRequest({
            url: 'project_management.api.client.create_project',
            method: 'POST',
            params: { data: this.form },
          })
        }
        this.$router.push('/projects')
      } catch (err) {
        this.error = err.message || 'Failed to save project'
      } finally {
        this.saving = false
      }
    },
  },
}
</script>
