<template>
  <div class="bg-white rounded-xl border border-gray-200 p-5">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-sm font-semibold text-gray-800">Purchases &amp; Invoices</h2>
      <Button
        v-if="!erpnextError"
        theme="blue" variant="solid"
        size="sm"
        icon-left="plus"
        :disabled="!canGenerate || working"
        @click="openCreateModal"
      >Generate Purchase Invoice</Button>
    </div>

    <p v-if="erpnextError" class="text-xs text-red-500">{{ erpnextError }}</p>

    <div v-else-if="loadingBilling" class="text-xs text-gray-400 text-center py-4">
      Loading purchase info...
    </div>

    <template v-else>
      <!-- Summary stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="rounded-lg border border-gray-200 bg-gray-50/60 p-3 text-center">
          <p class="text-lg font-bold text-gray-900">{{ billableCount }}</p>
          <p class="text-[10px] text-gray-500 mt-0.5">To Pay</p>
        </div>
        <div class="rounded-lg border border-blue-200 bg-blue-50/60 p-3 text-center">
          <p class="text-lg font-bold text-blue-700">{{ formatAmount(invoicedTotal) }}</p>
          <p class="text-[10px] text-blue-500 mt-0.5">Invoiced</p>
        </div>
        <div class="rounded-lg border border-green-200 bg-green-50/60 p-3 text-center">
          <p class="text-lg font-bold text-green-700">{{ formatAmount(paidTotal) }}</p>
          <p class="text-[10px] text-green-600 mt-0.5">Paid</p>
        </div>
        <div class="rounded-lg border border-amber-200 bg-amber-50/60 p-3 text-center">
          <p class="text-lg font-bold text-amber-700">{{ formatAmount(outstandingTotal) }}</p>
          <p class="text-[10px] text-amber-600 mt-0.5">Outstanding</p>
        </div>
      </div>

      <!-- Vendor list (table) -->
      <p class="text-[10px] uppercase tracking-wide text-gray-400 mb-1.5">Vendors</p>
      <div v-if="billing.vendor_rows?.length" class="rounded-lg border border-gray-200 overflow-hidden mb-4">
        <table class="w-full text-xs">
          <thead class="bg-gray-50 text-gray-500">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Vendor</th>
              <th class="text-left px-3 py-2 font-medium">Item</th>
              <th class="text-right px-3 py-2 font-medium">Amount</th>
              <th class="text-left px-3 py-2 font-medium">Billed</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="row in billing.vendor_rows" :key="row.name" class="hover:bg-gray-50/60">
              <td class="px-3 py-2">
                <p class="text-gray-800 font-medium">{{ row.vendor }}</p>
                <p v-if="row.supplier" class="text-[10px] text-gray-400">Supplier: {{ row.supplier }}</p>
              </td>
              <td class="px-3 py-2 text-gray-700">{{ row.item || '—' }}</td>
              <td class="px-3 py-2 text-right font-medium text-gray-800">{{ formatAmount(row.amount) }}</td>
              <td class="px-3 py-2">
                <Badge v-if="row.is_billed" label="Billed" theme="green" />
                <span v-else-if="(row.amount || 0) > 0" class="text-[10px] text-blue-600">Payable</span>
                <span v-else class="text-[10px] text-gray-400">&mdash;</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-xs text-gray-400 text-center py-2 mb-4">No vendors purchased on this project</p>

      <!-- Invoices table -->
      <p class="text-[10px] uppercase tracking-wide text-gray-400 mb-1.5">Purchase Invoices</p>
      <div v-if="billing.invoices?.length" class="rounded-lg border border-gray-200 overflow-hidden mb-2">
        <table class="w-full text-xs">
          <thead class="bg-gray-50 text-gray-500">
            <tr>
              <th class="text-left px-3 py-2 font-medium">Invoice</th>
              <th class="text-right px-3 py-2 font-medium">Total</th>
              <th class="text-left px-3 py-2 font-medium">Status</th>
              <th class="text-right px-3 py-2 font-medium"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="inv in billing.invoices"
              :key="inv.name"
              @click="openInvoiceDetail(inv.name)"
              class="cursor-pointer hover:bg-gray-50/60"
            >
              <td class="px-3 py-2">
                <p class="text-gray-800 font-medium">{{ inv.name }}</p>
                <p class="text-[10px] text-gray-400">{{ inv.posting_date }}</p>
              </td>
              <td class="px-3 py-2 text-right font-medium text-gray-800">{{ formatAmount(inv.grand_total) }}</td>
              <td class="px-3 py-2">
                <Badge :label="invoiceStatusLabel(inv.status)" :theme="invoiceStatusMap[inv.status] || 'gray'" />
              </td>
              <td class="px-3 py-2 text-right whitespace-nowrap">
                <Button
                  v-if="inv.status === 'Draft'"
                  size="sm" variant="outline"
                  :disabled="submitting"
                  @click.stop="submitInvoice(inv.name)"
                >Submit</Button>
                <FeatherIcon v-else name="chevron-right" class="w-4 h-4 text-gray-400 inline" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-xs text-gray-400 text-center py-2 mb-2">No purchase invoices yet</p>

      <p
        v-if="!billing.vendor_rows?.length"
        class="text-xs text-amber-600 mt-2"
      >Add vendors (with item + amount) on the project to enable purchase invoicing.</p>
    </template>

    <Dialog v-model="showCreateModal" :options="{ title: 'Generate Purchase Invoice', size: 'md' }">
      <template #body-content>
        <div class="space-y-4">
          <Autocomplete
            v-model="createForm.company"
            :options="config.companies"
            label="Company *"
            placeholder="Select company"
          />
          <Autocomplete
            v-model="createForm.currency"
            :options="config.currencies"
            label="Currency"
            placeholder="Select currency"
          />
          <Autocomplete
            v-model="createForm.item"
            :options="config.items"
            label="Item"
            placeholder="Default item for purchases"
          />
          <p class="text-xs text-gray-400">
            Will bill {{ billableCount }} vendor purchase(s) totaling {{ formatAmount(billableTotal) }}.
          </p>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Cancel</Button>
        <Button
          theme="blue" variant="solid"
          :loading="working"
          :loading-text="working ? 'Creating...' : null"
          @click="generateInvoice"
        >Create Purchase Invoice</Button>
      </template>
    </Dialog>

    <Dialog v-model="showDetailModal" :options="{ title: invoice?.name || 'Purchase Invoice Details', size: 'lg' }">
      <template #body-content>
        <div v-if="detailLoading" class="text-xs text-gray-400 text-center py-8">
          Loading invoice...
        </div>
        <div v-else-if="invoice">
          <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-100">
            <div class="text-xs text-gray-500 space-y-0.5">
              <p>Supplier: <span class="font-medium text-gray-800">{{ invoice.supplier_name || invoice.supplier }}</span></p>
              <p>Company: <span class="font-medium text-gray-800">{{ invoice.company }}</span></p>
              <p>Date: <span class="font-medium text-gray-800">{{ invoice.posting_date }}</span></p>
              <p v-if="invoice.due_date">Due: <span class="font-medium text-gray-800">{{ invoice.due_date }}</span></p>
            </div>
            <div class="text-right">
              <Badge :label="invoiceStatusLabel(invoice.status)" :theme="invoiceStatusMap[invoice.status] || 'gray'" />
              <p class="text-sm font-bold text-gray-900 mt-1">{{ formatAmount(invoice.grand_total) }}</p>
            </div>
          </div>

          <p class="text-[10px] uppercase tracking-wide text-gray-400 mb-1">Items</p>
          <div class="rounded-lg border border-gray-200 overflow-hidden mb-4">
            <table class="w-full text-xs">
              <thead class="bg-gray-50 text-gray-500">
                <tr>
                  <th class="text-left px-3 py-2 font-medium">Item</th>
                  <th class="text-right px-3 py-2 font-medium">Qty</th>
                  <th class="text-right px-3 py-2 font-medium">Rate</th>
                  <th class="text-right px-3 py-2 font-medium">Amount</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="(it, idx) in invoice.items" :key="idx">
                  <td class="px-3 py-2 text-gray-800">
                    {{ it.item_name || it.item_code }}
                    <p v-if="it.description && it.description !== it.item_code" class="text-[10px] text-gray-400">{{ it.description }}</p>
                  </td>
                  <td class="px-3 py-2 text-right text-gray-700 truncate">{{ it.qty }} {{ it.uom || '' }}</td>
                  <td class="px-3 py-2 text-right text-gray-700">{{ formatAmount(it.rate) }}</td>
                  <td class="px-3 py-2 text-right font-medium text-gray-800">{{ formatAmount(it.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="flex justify-end mb-4">
            <div class="w-52 space-y-1 text-xs">
              <div class="flex justify-between text-gray-600">
                <span>Net Total</span>
                <span>{{ formatAmount(invoice.net_total) }}</span>
              </div>
              <div class="flex justify-between text-gray-600">
                <span>Taxes</span>
                <span>{{ formatAmount(invoice.total_taxes_and_charges) }}</span>
              </div>
              <div class="flex justify-between font-semibold text-gray-900 border-t border-gray-100 pt-1">
                <span>Grand Total</span>
                <span>{{ formatAmount(invoice.grand_total) }}</span>
              </div>
              <div class="flex justify-between text-gray-600">
                <span>Outstanding</span>
                <span class="text-amber-600">{{ formatAmount(invoice.outstanding_amount) }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Close</Button>
        <Button
          v-if="invoice && invoice.status === 'Draft'"
          theme="blue" variant="solid"
          :loading="submitting"
          :loading-text="submitting ? 'Submitting...' : null"
          @click="submitInvoice(invoice.name)"
        >Submit Invoice</Button>
        <Button
          v-if="invoice"
          variant="ghost" @click="openInDesk(invoice.name)"
        >Open in ERPNext</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { frappeRequest, Button, Badge, Dialog, Autocomplete, LoadingIndicator, FeatherIcon, toast } from 'frappe-ui'

export default {
  name: 'PurchaseSection',
  components: { Button, Badge, Dialog, Autocomplete, LoadingIndicator, FeatherIcon },
  props: {
    projectId: { type: String, required: true },
  },
  data() {
    return {
      config: { companies: [], currencies: [], items: [], suppliers: [], default_currency: '' },
      billing: { vendor_rows: [], invoices: [], billing_company: '', billing_currency: '' },
      loadingBilling: true,
      erpnextError: '',
      working: false,
      submitting: false,
      showCreateModal: false,
      showDetailModal: false,
      detailLoading: false,
      invoice: null,
      createForm: {
        company: '',
        currency: '',
        item: '',
      },
      invoiceStatusMap: {
        Draft: 'gray',
        Submitted: 'blue',
        Paid: 'green',
        Unpaid: 'amber',
        'Partly Paid': 'amber',
        Overdue: 'red',
        Cancelled: 'red',
        Return: 'red',
        'Credit Note Issued': 'amber',
      },
    }
  },
  computed: {
    billableRows() {
      return (this.billing.vendor_rows || []).filter(
        (r) => !r.is_billed && (r.amount || 0) > 0
      )
    },
    billableCount() {
      return this.billableRows.length
    },
    billableTotal() {
      return this.billableRows.reduce((sum, r) => sum + (r.amount || 0), 0)
    },
    activeInvoices() {
      return (this.billing.invoices || []).filter((i) => i.status !== 'Cancelled')
    },
    invoicedTotal() {
      return this.activeInvoices.reduce((sum, i) => sum + (i.grand_total || 0), 0)
    },
    paidTotal() {
      return this.activeInvoices.reduce((sum, i) => {
        const outstanding = i.outstanding_amount || 0
        return sum + Math.max(0, (i.grand_total || 0) - outstanding)
      }, 0)
    },
    outstandingTotal() {
      return this.activeInvoices.reduce((sum, i) => sum + (i.outstanding_amount || 0), 0)
    },
    canGenerate() {
      return this.billableCount > 0
    },
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loadingBilling = true
      this.erpnextError = ''
      try {
        const res = await frappeRequest({
          url: 'project_management.api.purchasing.get_purchase_billing',
          method: 'POST',
          params: { project: this.projectId },
        })
        this.billing = res
        this.config = res.config || this.config
        if (!this.createForm.company) this.createForm.company = this.billing.billing_company
        if (!this.createForm.currency) this.createForm.currency = this.billing.billing_currency || this.config.default_currency
        if (!this.createForm.item && this.config.items?.length) this.createForm.item = this.config.items[0].value
      } catch (err) {
        this.erpnextError = err.message || 'ERPNext integration is not available'
      } finally {
        this.loadingBilling = false
      }
    },
    formatAmount(value) {
      const num = Number(value || 0)
      const currency = this.billing.billing_currency || this.config.default_currency || ''
      return new Intl.NumberFormat(undefined, { style: 'currency', currency: currency || undefined }).format(num)
    },
    invoiceStatusLabel(status) {
      if (status === 'Submitted' && this.invoice && !this.invoice.outstanding_amount) return 'Paid'
      return status
    },
    openCreateModal() {
      this.showCreateModal = true
    },
    async generateInvoice() {
      if (!this.createForm.company) {
        toast({ title: 'Error', text: 'Please select a company', icon: 'alert-circle', iconClasses: 'text-red-600' })
        return
      }
      this.working = true
      try {
        const res = await frappeRequest({
          url: 'project_management.api.purchasing.create_purchase_invoice',
          method: 'POST',
          params: {
            project: this.projectId,
            data: {
              company: this.createForm.company,
              currency: this.createForm.currency,
              item: this.createForm.item,
            },
          },
        })
        this.showCreateModal = false
        const invoices = res.invoices || []
        const names = invoices.map(i => i.name).join(', ')
        toast({
          title: 'Success',
          text: invoices.length > 1
            ? `${invoices.length} Purchase Invoices created: ${names}`
            : `Purchase Invoice ${names} created`,
          icon: 'check-circle',
          iconClasses: 'text-green-600',
        })
        this.loadAll()
        this.$emit('invoice-created')
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to create purchase invoice', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.working = false
      }
    },
    async openInvoiceDetail(name) {
      this.detailLoading = true
      this.showDetailModal = true
      this.invoice = null
      try {
        const res = await frappeRequest({
          url: 'project_management.api.purchasing.get_purchase_invoice',
          method: 'POST',
          params: { name },
        })
        this.invoice = res
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to load invoice', icon: 'alert-circle', iconClasses: 'text-red-600' })
        this.showDetailModal = false
      } finally {
        this.detailLoading = false
      }
    },
    async submitInvoice(name) {
      this.submitting = true
      try {
        const res = await frappeRequest({
          url: 'project_management.api.purchasing.submit_purchase_invoice',
          method: 'POST',
          params: { name },
        })
        toast({ title: 'Success', text: `Purchase Invoice ${res.name} submitted`, icon: 'check-circle', iconClasses: 'text-green-600' })
        if (this.invoice && this.invoice.name === name) {
          this.invoice = res
        }
        this.loadAll()
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to submit invoice', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.submitting = false
      }
    },
    openInDesk(name) {
      window.open(`/app/purchase-invoice/${name}`, '_blank')
    },
  },
}
</script>
