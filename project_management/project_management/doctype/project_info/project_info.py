# Copyright (c) 2026, Paras Gogia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectInfo(Document):

    def after_insert(self):
        workspace = self.create_raven_workspace()

        if workspace:
            # Add Project users to the Raven Workspace
            self.sync_workspace_members()

            # Create project channels and add channel-specific members
            self.create_internal_channel(workspace)
            self.create_external_channel(workspace)
            self.create_discussion_channel(workspace)

    def on_update(self):
        if self.is_new():
            return

        if not self.raven_workspace:
            return

        # Sync workspace-level membership
        self.sync_workspace_members()

        # Sync channel-level membership
        self.sync_internal_channel()
        self.sync_external_channel()
        self.sync_discussion_channel()

    def on_trash(self):
        self._delete_raven_docs()
        self._delete_linked_project_docs()

    # ----------------------------------------------------
    # Cascade Delete
    # ----------------------------------------------------

    def _delete_raven_docs(self):
        if not frappe.db.exists("DocType", "Raven Channel"):
            return

        channels = frappe.get_all(
            "Raven Channel",
            filters={
                "linked_doctype": "Project Info",
                "linked_document": self.name
            },
            pluck="name"
        )

        for channel in channels:
            frappe.delete_doc(
                "Raven Channel",
                channel,
                ignore_permissions=True
            )

        if (
            self.raven_workspace
            and frappe.db.exists("Raven Workspace", self.raven_workspace)
        ):
            frappe.db.set_value(
                "Project Info",
                self.name,
                "raven_workspace",
                None
            )

            frappe.delete_doc(
                "Raven Workspace",
                self.raven_workspace,
                ignore_permissions=True
            )

    def _delete_linked_project_docs(self):
        for doctype, fieldname in [
            ("Time Log", "project"),
            ("Project Task", "project"),
            ("Deliverable", "project"),
        ]:
            for name in frappe.get_all(
                doctype,
                filters={fieldname: self.name},
                pluck="name"
            ):
                frappe.delete_doc(
                    doctype,
                    name,
                    ignore_permissions=True
                )

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

            self.db_set(
                "raven_workspace",
                workspace.name
            )

            return workspace

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to create Raven Workspace for {self.name}"
            )

            return None

    # ----------------------------------------------------
    # Workspace Members
    # ----------------------------------------------------

    def get_workspace_members(self):
        """
        Return all users who should have access
        to this project's Raven workspace.
        """

        members = set()

        # Project Manager
        if self.project_manager:
            members.add(self.project_manager)

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.add(row.user)

        # Client
        if self.client:
            members.add(self.client)

        # Vendors
        for row in self.vendors:
            if row.vendor:
                vendor = frappe.get_doc(
                    "Vendor",
                    row.vendor
                )

                if vendor.user:
                    members.add(vendor.user)

        return members

    def sync_workspace_members(self):
        """
        Keep Raven Workspace Members synchronized
        with the users associated with this project.
        """

        if not self.raven_workspace:
            return

        if not frappe.db.exists(
            "Raven Workspace",
            self.raven_workspace
        ):
            return

        desired_members = self.get_workspace_members()

        workspace = frappe.get_doc(
            "Raven Workspace",
            self.raven_workspace
        )

        # ------------------------------------------------
        # Workspace owner must always remain a member
        # ------------------------------------------------

        if workspace.owner:
            desired_members.add(workspace.owner)

        # ------------------------------------------------
        # Only users who exist as Raven Users can be
        # added to Raven Workspace Member.
        # ------------------------------------------------

        raven_members = set()

        for user in desired_members:
            if frappe.db.exists(
                "Raven User",
                {"user": user}
            ):
                raven_members.add(user)

        # ------------------------------------------------
        # Get current workspace members
        # ------------------------------------------------

        current_members = frappe.get_all(
            "Raven Workspace Member",
            filters={
                "workspace": self.raven_workspace
            },
            fields=[
                "name",
                "user",
                "is_admin"
            ]
        )

        current_users = {
            member.user
            for member in current_members
        }

        # ------------------------------------------------
        # Add missing workspace members
        # ------------------------------------------------

        for user in raven_members:
            if user not in current_users:
                member = frappe.get_doc({
                    "doctype": "Raven Workspace Member",
                    "workspace": self.raven_workspace,
                    "user": user,
                    "is_admin": 0
                })

                member.insert(
                    ignore_permissions=True
                )

        # ------------------------------------------------
        # Remove old workspace members
        # ------------------------------------------------

        for member in current_members:

            # Never remove workspace owner
            if member.user == workspace.owner:
                continue

            if member.user not in raven_members:

                frappe.delete_doc(
                    "Raven Workspace Member",
                    member.name,
                    ignore_permissions=True
                )

    # ----------------------------------------------------
    # Channels
    # ----------------------------------------------------

    def create_internal_channel(self, workspace):

        try:
            channel = frappe.get_doc({
                "doctype": "Raven Channel",
                "channel_name": "internal",
                "channel_description": (
                    f"Internal discussion for {self.project_name}"
                ),
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
                "channel_description": (
                    f"External discussion for {self.project_name}"
                ),
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
                "channel_description": (
                    f"Discussion for {self.project_name}"
                ),
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

        # Project Manager
        if self.project_manager:
            members.append(self.project_manager)

        # Project Members
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

        # Vendors
        for row in self.vendors:
            if row.vendor:

                vendor = frappe.get_doc(
                    "Vendor",
                    row.vendor
                )

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

    def _find_channel(self, channel_name):
        """
        Find a channel in this project's Raven workspace
        by its plain name.
        """

        if not self.raven_workspace:
            return None

        names = frappe.get_all(
            "Raven Channel",
            filters={
                "workspace": self.raven_workspace,
                "channel_name": channel_name,
            },
            pluck="name",
            limit=1,
        )

        if not names:
            return None

        return frappe.get_doc(
            "Raven Channel",
            names[0]
        )

    def sync_channel_members(self, channel, desired_members):

        desired_members = list(set(desired_members))

        current_members = frappe.get_all(
            "Raven Channel Member",
            filters={
                "channel_id": channel.name
            },
            fields=[
                "name",
                "user_id"
            ]
        )

        current_users = [
            member.user_id
            for member in current_members
        ]

        # -----------------------
        # Add Missing Members
        # -----------------------

        new_members = [
            user
            for user in desired_members
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

        channel = self._find_channel("internal")

        if not channel:
            return

        members = []

        # Project Manager
        if self.project_manager:
            members.append(self.project_manager)

        # Project Members
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

        channel = self._find_channel("external")

        if not channel:
            return

        members = []

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.append(row.user)

        # Vendors
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

    # ----------------------------------------------------
    # Discussion Sync
    # ----------------------------------------------------

    def sync_discussion_channel(self):

        channel = self._find_channel("discussion")

        if not channel:
            return

        members = set()

        # Project Members
        for row in self.project_members:
            if row.user and row.is_active:
                members.add(row.user)

        # Client
        if self.client:
            members.add(self.client)

        self.sync_channel_members(
            channel,
            list(members)
        )
