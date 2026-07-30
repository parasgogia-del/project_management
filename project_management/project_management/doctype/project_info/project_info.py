# Copyright (c) 2026, Paras Gogia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectInfo(Document):

    def after_insert(self):
        workspace = self.create_raven_workspace()

        if workspace:
            self.create_internal_channel(workspace)
            self.create_external_channel(workspace)
            self.create_discussion_channel(workspace)

    def on_update(self):
        if self.is_new():
            return

        if not self.raven_workspace:
            return

        self.sync_internal_channel()
        self.sync_external_channel()
        self.sync_discussion_channel()

    # ----------------------------------------------------
    # Workspace
    # ----------------------------------------------------

    def create_raven_workspace(self):
        try:
            workspace = frappe.get_doc({
                "doctype": "Raven Workspace",
                "workspace_name": self.project_name,
                "type": "Private",
                "description": f"Workspace for project {self.project_name}"
            })

            workspace.insert()

            self.db_set("raven_workspace", workspace.name)

            return workspace

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to create Raven Workspace for {self.name}"
            )
            return None

    # ----------------------------------------------------
    # Channels
    # ----------------------------------------------------

    def create_internal_channel(self, workspace):

        try:
            channel = frappe.get_doc({
                "doctype": "Raven Channel",
                "channel_name": "internal",
                "channel_description": f"Internal discussion for {self.project_name}",
                "workspace": workspace.name,
                "type": "Private",
                "linked_doctype": "Project Info",
                "linked_document": self.name,
            })

            channel.insert()

            self.add_internal_members(channel)

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to create Internal Channel for {self.name}"
            )

    def create_external_channel(self, workspace):

        try:

            channel = frappe.get_doc({
                "doctype": "Raven Channel",
                "channel_name": "external",
                "channel_description": f"External discussion for {self.project_name}",
                "workspace": workspace.name,
                "type": "Private",
                "linked_doctype": "Project Info",
                "linked_document": self.name,
            })

            channel.insert()

            self.add_external_members(channel)

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to create External Channel for {self.name}"
            )

    def create_discussion_channel(self, workspace):
        try:

            channel = frappe.get_doc({
            "doctype": "Raven Channel",
            "channel_name": "discussion",
            "channel_description": f"Discussion for {self.project_name}",
            "workspace": workspace.name,
            "type": "Private",
            "linked_doctype": "Project Info",
            "linked_document": self.name,
        })

            channel.insert()

            self.add_discussion_members(channel)

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to create Discussion Channel for {self.name}"
            )

    # ----------------------------------------------------
    # Initial Members
    # ----------------------------------------------------

    def add_internal_members(self, channel):

        members = []

        if self.project_manager:
            members.append(self.project_manager)

        for row in self.project_members:

            if row.user and row.is_active:
                members.append(row.user)

        members = list(set(members))

        channel.add_members(members)

    def add_external_members(self, channel):

        members = []

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.append(row.user)

        for row in self.vendors:

            if row.vendor:

                vendor = frappe.get_doc("Vendor", row.vendor)

                if vendor.user:
                    members.append(vendor.user)

        members = list(set(members))

        channel.add_members(members)


    def add_discussion_members(self, channel):

        members = set()

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.add(row.user)

        # Client
        if self.client:
            members.add(self.client)

        channel.add_members(list(members))

    # ----------------------------------------------------
    # Sync Helpers
    # ----------------------------------------------------

    def sync_channel_members(self, channel, desired_members):

        desired_members = list(set(desired_members))

        current_members = frappe.get_all(
            "Raven Channel Member",
            filters={
                "channel_id": channel.name
            },
            fields=["name", "user_id"]
        )

        current_users = [m.user_id for m in current_members]

        # -----------------------
        # Add Missing Members
        # -----------------------

        new_members = [
            user for user in desired_members
            if user not in current_users
        ]

        if new_members:
            channel.add_members(new_members)

        # -----------------------
        # Remove Old Members
        # -----------------------

        for member in current_members:

            # Keep Administrator
            if member.user_id == "Administrator":
                continue

            if member.user_id not in desired_members:

                frappe.delete_doc(
                    "Raven Channel Member",
                    member.name,
                    ignore_permissions=True
                )

    # ----------------------------------------------------
    # Internal Sync
    # ----------------------------------------------------

    def sync_internal_channel(self):

        channel_name = f"{self.project_name}-internal"

        if not frappe.db.exists("Raven Channel", channel_name):
            return

        channel = frappe.get_doc(
            "Raven Channel",
            channel_name
        )

        members = []

        if self.project_manager:
            members.append(self.project_manager)

        for row in self.project_members:

            if row.user and row.is_active:
                members.append(row.user)

        self.sync_channel_members(
            channel,
            members
        )

    # ----------------------------------------------------
    # External Sync
    # ----------------------------------------------------

    def sync_external_channel(self):

        channel_name = f"{self.project_name}-external"

        if not frappe.db.exists("Raven Channel", channel_name):
            return

        channel = frappe.get_doc(
            "Raven Channel",
            channel_name
        )

        members = []

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.append(row.user)


        for row in self.vendors:

            if row.vendor:

                vendor = frappe.get_doc(
                    "Vendor",
                    row.vendor
                )

                if vendor.user:
                    members.append(vendor.user)

        self.sync_channel_members(
            channel,
            members
        )

    def sync_discussion_channel(self):

        channel_name = f"{self.raven_workspace}-discussion"

        if not frappe.db.exists("Raven Channel", channel_name):
            return

        channel = frappe.get_doc("Raven Channel", channel_name)

        members = set()

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.add(row.user)

        # Client
        if self.client:
            members.add(self.client)

        self.sync_channel_members(channel, list(members))
