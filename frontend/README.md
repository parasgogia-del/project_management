# Project Management System

A web application for managing projects, deliverables, and tasks with dedicated portals for project managers, team members, clients, and vendors.

This repository contains the **frontend application** — a Vue 3 + Vite + Frappe UI SPA that talks to an existing **Frappe backend**. All business logic, DocTypes, workflows, permissions, and APIs live in the backend; this frontend consumes those APIs.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [User Roles](#user-roles)
- [Application Flow](#application-flow)
- [Role-Based Application Flow](#role-based-application-flow)
- [Frontend Architecture](#frontend-architecture)
- [Project Structure](#project-structure)
- [Pages / Screens](#pages--screens)
- [Components](#components)
- [API Integration](#api-integration)
- [Backend Integration](#backend-integration)
- [Workflow](#workflow)
- [Project Progress Flow](#project-progress-flow)
- [Task and Deliverable Relationship](#task-and-deliverable-relationship)
- [Authentication](#authentication)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Development Workflow](#development-workflow)
- [Screenshots](#screenshots)
- [Complete User Journey](#complete-user-journey)
- [Feature-to-Page Mapping](#feature-to-page-mapping)
- [Technologies Used](#technologies-used)
- [Design System / UI](#design-system--ui)
- [Responsive Design](#responsive-design)
- [Error Handling / Loading States](#error-handling--loading-states)
- [Future Improvements](#future-improvements)
- [Contribution](#contribution)
- [License](#license)

---

## Project Overview

**Project Management System** is a project delivery workspace where teams plan projects, break them down into **deliverables**, and manage the **tasks** needed to complete them.

The application solves a coordination problem: clients, managers, team members, and external vendors all need to follow a project through its lifecycle — from planning to delivery, approval, and rework — without losing track of progress, time, comments, or files.

### Who uses it

| Role             | How they use it                                             |
| ---------------- | ----------------------------------------------------------- |
| Project Manager  | Creates and runs projects, assigns work, tracks everything  |
| Project Member   | Executes tasks, logs time, submits deliverables for approval |
| Client           | Reviews deliverables, approves them or requests changes     |
| Vendor           | Fulfils assigned tasks and submits completed deliverables   |

### What the frontend is responsible for

- Rendering all screens (dashboards, lists, detail views, forms, Gantt chart, reports)
- Role-based routing and navigation
- Calling backend APIs to read and update data
- Client-side filtering, progress display, and feedback

### How it communicates with the Frappe backend

The frontend is a **same-origin SPA** served by Frappe. It makes `frappeRequest` (Axios-based) calls to **whitelisted Frappe API methods** under `project_management.api.*`, using the session cookie and a CSRF token for authentication. It never touches the database directly.

---

## Key Features

- **Project management** — create, edit, view, and delete projects; assign a client, manager, members, and vendors
- **Manager dashboard** — overview stats, project progress, daily/weekly progress report, recent tasks, quick actions
- **Deliverable management** — create deliverables under a project and drive them through an approval workflow
- **Task management** — create/edit tasks with assignee, vendor, priority, dates, and estimated hours
- **Task status management** — `Open`, `Working`, `Blocked`, `Completed`
- **Deliverable workflow** — `Draft → WIP → Ready for Approval → Awaiting Client Review → Approved / Changes Requested`
- **Project progress tracking** — percentage progress computed from completed tasks
- **Time logging** — log hours against a task; view per-task logs and today's total hours
- **Today's Focus** — members star tasks to pin them to a daily focus list
- **Comments** — add, edit, and delete comments on projects, deliverables, and tasks
- **Attachments** — upload/download files on projects, deliverables, and tasks
- **Gantt chart** — visual timeline of task schedules for a project
- **Reports** — daily/weekly progress reports per project
- **Reminders** — Automated task reminders via Raven: DMs the assignee when a task is overdue or due soon, with per-project enable/disable and reminder-window settings.
- **Member portal** — dashboard of my tasks, my projects, my deliverables, and today's focus
- **Client portal** — dashboard of my projects and deliverables, plus review/approval actions
- **Vendor portal** — dashboard of assigned tasks/deliverables and delivery submission
- **Authentication** — login, registration, and role-based screen access
- **Role-based screens** — separate navigation and routes per role

---

## User Roles

The application has four roles, enforced in the backend by Frappe permissions and mirrored in the frontend router guard and sidebar.

### Project Manager

- Create, edit, and delete projects
- Assign clients, project managers, members, and vendors to a project
- Create deliverables and tasks
- Advance deliverables through the approval workflow (`Start Work`, `Send for Approval`)
- Update task status, edit tasks, log time
- View Gantt charts and daily/weekly reports
- Access every portal for visibility

### Project Member

- View projects and deliverables they are part of
- See tasks assigned to them on a personal dashboard
- Update task status (`Open`, `Working`, `Blocked`, `Completed`)
- Log time against tasks
- Star tasks for "Today's Focus"
- Drive deliverables: `Start Work`, `Submit for Approval`, `Start Rework`
- Comment and attach files

### Client

- View the projects and deliverables associated with their account
- Review deliverables in `Awaiting Client Review`
- `Approve` a deliverable or `Request Changes` (optionally with feedback comment)
- View tasks, progress, members, files, and comments
- Invite members to a project

### Vendor

- View projects, deliverables, and tasks assigned to their vendor account
- Update task status and log time
- `Start Work` / `Start Rework` on deliverables
- `Submit Delivery` with an attached file and delivery note/access link

---

## Application Flow

```mermaid
flowchart TD
    A[User opens application] --> B{Logged in?}
    B -->|No| C[Login / Register]
    C --> B
    B -->|Yes| D[Role-based landing page]
    D --> E[Dashboard]
    E --> F[Projects / Deliverables / Tasks]
    F --> G[Detail Pages]
    G --> H[Comments / Attachments / Time Logs]
```

In practice the flow is:

```mermaid
flowchart TD
    A[User] --> B[Authentication]
    B --> C[Dashboard]
    C --> D[Projects]
    D --> E[Project Details]
    E --> F[Tasks]
    E --> G[Deliverables]
    F --> H[Task Details]
    G --> I[Deliverable Details]
    H --> J[Comments / Attachments / Time Logs]
    I --> J
    I --> K[Client Review / Approval]
```

---

## Role-Based Application Flow

### Project Manager Flow

```mermaid
flowchart TD
    A[Login] --> B[Manager Dashboard /]
    B --> C[Projects /projects]
    C --> D[Create Project /project/new]
    C --> E[Project Details /project/:id]
    E --> F[Tasks /project/:id/tasks]
    E --> G[Deliverables /project/:id/deliverables]
    E --> H[Gantt Chart /project/:id/gantt]
    E --> I[Reports /project/:id/reports]
    F --> J[Task Detail /task/:id]
    G --> K[Deliverable Detail /deliverable/:id]
```

### Project Member Flow

```mermaid
flowchart TD
    A[Login] --> B[Member Dashboard /member/dashboard]
    B --> C[My Projects /member/project/:id]
    B --> D[My Deliverables /member/deliverable/:id]
    B --> E[My Tasks /member/task/:id]
    E --> F[Update Status / Log Time / Focus]
    D --> G[Start Work / Submit for Approval / Start Rework]
```

### Client Flow

```mermaid
flowchart TD
    A[Login] --> B[Client Dashboard /client/dashboard]
    B --> C[My Projects /client/project/:id]
    B --> D[My Deliverables /client/deliverable/:id]
    C --> E[Project Details]
    D --> F[Review Actions]
    F --> G[Approve]
    F --> H[Request Changes + Feedback]
    C --> I[Task View /client/task/:id]
```

### Vendor Flow

```mermaid
flowchart TD
    A[Login] --> B[Vendor Dashboard /vendor/dashboard]
    B --> C[Assigned Projects /vendor/project/:id]
    B --> D[Assigned Tasks /vendor/task/:id]
    B --> E[My Deliverables /vendor/deliverable/:id]
    D --> F[Update Status / Log Time]
    E --> G[Start Work / Start Rework]
    E --> H[Submit Delivery + File]
```

---

## Frontend Architecture

```mermaid
flowchart TD
    A[Vue Components] --> B[Pages / Views]
    B --> C[Vue Router]
    B --> D[Data Layer - frappe-ui Resources]
    D --> E[frappeRequest / HTTP]
    E --> F[Frappe REST / Whitelisted APIs]
    F --> G[Frappe Backend]
    G --> H[Database / DocTypes]
```

| Layer                    | Responsibility                                                        |
| ------------------------ | --------------------------------------------------------------------- |
| Vue Components           | Reusable UI pieces (`ProgressBar`, `CommentSection`, `FileUpload`...)  |
| Pages / Views            | Route-level screens under `src/pages/`                                 |
| Vue Router               | Declares routes and enforces role-based guards                         |
| Data layer               | `src/data/` — frappe-ui `createResource` factories + session state     |
| `frappeRequest` (HTTP)   | Frappe UI's Axios wrapper that calls `/api/method/...`                 |
| Frappe whitelisted APIs  | Backend endpoints in `project_management.api.*`                        |
| Frappe backend           | DocTypes, workflows, permissions, and business logic                   |

Every page fetches data through either a **resource** from `src/data/resources.js` (e.g. `useProject`, `useTasks`) or a direct `frappeRequest` call. No page calls the Frappe API by URL string everywhere — all endpoints are centralized in the data layer and page scripts.

---

## Project Structure

```text
frontend/
├── docs/
│   └── screenshots/          # Screenshot images for the README
├── public/                   # (dev) static public assets
├── src/
│   ├── components/
│   │   ├── layout/           # App shell: AppLayout, Sidebar, Topbar
│   │   ├── ActivityTimeline.vue
│   │   ├── CommentSection.vue
│   │   ├── EmptyState.vue
│   │   ├── FileUpload.vue
│   │   └── ProgressBar.vue
│   ├── data/
│   │   ├── resources.js      # frappe-ui resource factories (all API calls)
│   │   ├── session.js        # session user, roles, portal routing helper
│   │   └── store.js          # tiny reactive global store
│   ├── pages/
│   │   ├── client/           # Client portal screens
│   │   ├── manager/          # Project Manager screens
│   │   ├── member/           # Project Member portal screens
│   │   ├── vendor/           # Vendor portal screens
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   └── NoAccess.vue
│   ├── utils/
│   │   └── statusColors.js   # status -> badge colour mapping
│   ├── App.vue               # Root component (router-view + ToastProvider)
│   ├── index.css             # Tailwind/Frappe UI entry styles
│   ├── main.js               # App bootstrap
│   └── router.js             # Route table + auth/role guards
├── index.html                # HTML shell + CSRF token bootstrap
├── package.json
├── postcss.config.js
├── tailwind.config.js        # Extends frappe-ui/tailwind preset
├── vite.config.mjs           # Vite + Frappe UI plugin config
└── README.md
```

## Backend Integration

```mermaid
flowchart LR
    A[Vue 3 Frontend] --> B[Frappe UI]
    A --> C[API Layer]
    C --> D[Frappe Backend]
    D --> E[DocTypes]
    D --> F[Database]
```

The frontend consumes existing Frappe APIs and never re-implements business logic.

- **Frontend responsibilities:** rendering, routing, role-based UI, form capture, client-side filtering, calling APIs, showing progress/errors.
- **Backend responsibilities:** DocTypes (`Project Info`, `Deliverable`, `Project Task`, `Project Member`, `Project Vendors`, `Vendor`, `Deliverable Task`, `Time Log`), permissions, the deliverable workflow, data validation, and calculations (e.g. progress percentages).

The deliverables' workflow is executed on the backend through Frappe's `apply_workflow`; the frontend simply sends the chosen action name.

---

## Workflow

### Deliverable workflow

States (as defined in the backend `Deliverable` doctype): `Draft`, `WIP`, `Ready for Approval`, `Awaiting Client Review`, `Approved`, `Changes Requested`.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> WIP: Start Work
    WIP --> ReadyForApproval: Submit for Approval
    ReadyForApproval --> AwaitingClientReview: Send for Approval
    AwaitingClientReview --> Approved: Approve
    AwaitingClientReview --> ChangesRequested: Request Changes
    ChangesRequested --> WIP: Start Rework
    Approved --> [*]
```

Actions shown per role in the frontend:

| Role            | Available actions                                        |
| --------------- | -------------------------------------------------------- |
| Project Manager | `Start Work`, `Send for Approval`                        |
| Project Member  | `Start Work`, `Submit for Approval`, `Start Rework`      |
| Client          | `Approve`, `Request Changes` (when `Awaiting Client Review`) |
| Vendor          | `Start Work`, `Start Rework`, `Submit Delivery`          |

### Task workflow

Tasks use a simple status model: `Open → Working → Blocked → Completed`. Any status can be set directly from the task detail page, subject to backend permissions.

---

## Task and Deliverable Relationship

A project contains deliverables, and each deliverable contains tasks. Tasks belong to exactly one deliverable (and therefore one project).

```mermaid
erDiagram
    PROJECT ||--o{ DELIVERABLE : contains
    DELIVERABLE ||--o{ TASK : contains
    PROJECT ||--o{ TASK : contains
    TASK ||--o{ TIME_LOG : has
    PROJECT ||--o{ PROJECT_MEMBER : has
    PROJECT ||--o{ PROJECT_VENDORS : has
```

---

## Authentication

- **Login** — the Login page posts to the standard Frappe `login` endpoint (`usr`/`pwd`) and reloads the page. Login is only functional when served on the Frappe domain.
- **Session** — `src/data/session.js` fetches the session user via `get_session_user` and exposes `user`, `roles`, and `isLoggedIn` reactively.
- **Router guard** — every navigation first resolves the session. Unauthenticated users are sent to `/login`. Public routes (`/login`, `/register`) are whitelisted with `meta.public`.
- **Role guard** — routes declare `meta.roles` (e.g. `['Project Manager']`). If the user's roles don't match, they are redirected to their portal or `/no-access`.
- **Portal routing** — `getPortal()` maps role → landing page:
  - `Client` → `/client/dashboard`
  - `Project Manager` → `/`
  - `Project Member` → `/member/dashboard`
  - `Vendor` → `/vendor/dashboard`
- **CSRF** — `index.html` fetches a CSRF token on boot (`get_csrf_token`) and stores it in `window.csrf_token`, used by file uploads.
- **Logout** — posts to `logout` then redirects to `/project_management/login`.

---

## Installation

### Prerequisites

- **Node.js** (project uses Vite 5)
- **npm**
- A running **Frappe / Bench** environment with the `project_management` app installed, migrated, and serving a site
- Backend site URL reachable on the same origin as the frontend

### Clone Repository

```bash
git clone <repository-url>
cd project_management/frontend
```

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The Vite dev server runs on **port 8080** (`http://localhost:8080`).

### Build for Production

```bash
npm run build
```

The production build outputs a manifest into `../project_management/public/frontend`, from which Frappe serves the app under `/assets/project_management/frontend/`.

---

## Environment Configuration

The frontend currently has **no `.env` files and no environment variables**. API calls are made to relative same-origin paths (`/api/method/...`), so no base-URL configuration is required.

> **Note for development:** because calls are same-origin, the dev server must reach the Frappe backend at `/api/...`. In this setup the app is intended to be served by Frappe itself (see the build output path in `vite.config.mjs`).

No secrets, tokens, or credentials are stored in the repository.

---

## Development Workflow

1. Start the Frappe backend and ensure the `project_management` app is installed and migrated.
2. Start the frontend dev server (`npm run dev`, port 8080) — or build and serve via Frappe.
3. Open the application in your browser.
4. Log in (or register a new account as Member/Client/Vendor).
5. You land on the dashboard for your role.
6. Project Managers: create projects, deliverables, and tasks; assign members/vendors.
7. Members/Vendors: work on tasks, log time, update status, and submit deliverables.
8. Clients: review deliverables and approve or request changes.

---

## Screenshots

### Login

<img width="1857" height="1093" alt="Screenshot from 2026-08-07 16-36-25" src="https://github.com/user-attachments/assets/bc742ac3-2e29-4a2f-85bd-329d6c03a3ac" />

### Manager Dashboard

<img width="1857" height="1124" alt="Screenshot from 2026-08-07 16-45-54" src="https://github.com/user-attachments/assets/73d7c255-95c8-491e-a530-a681bef705d2" />

### Projects

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/8e26f263-4f28-462c-b1b7-cf5e019e5f9f" />


### Project Details

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/3c414989-503c-4886-8c10-120c8632d4a1" />

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/2c87b789-d6aa-44c0-bb8b-e669174ada8a" />

### Tasks

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/671be355-00cf-49e1-b077-79c8ae5abd49" />

### Deliverables

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/eca8a251-d2d2-4d39-928b-6365eddb923d" />

### Gantt Chart

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/c7b8cf16-629c-4a3b-ae46-dd66176af9c7" />

### Member Portal

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/09d52294-9fe4-43fd-a7fe-436786fb4433" />

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/c2e0cc5f-7855-492d-8e7b-3617b97b2e0a" />

### Client Portal

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/82e39942-92fe-4668-9deb-da5b1a97a178" />

### Vendor Portal

<img width="1857" height="1124" alt="image" src="https://github.com/user-attachments/assets/893510e8-388a-454c-9ff2-a82a307f0bb9" />

---

## Complete User Journey

```mermaid
flowchart TD
    A[User Opens Application] --> B[Login]
    B --> C{User Role}

    C -->|Project Manager| D[Manager Dashboard]
    C -->|Client| E[Client Dashboard]
    C -->|Vendor| F[Vendor Dashboard]
    C -->|Project Member| G[Member Dashboard]

    D --> H[Projects]
    H --> I[Project Details]
    I --> J[Tasks]
    I --> K[Deliverables]

    J --> L[Task Details]
    K --> M[Deliverable Details]

    L --> N[Comments]
    L --> O[Time Logs]
    L --> P[Attachments]

    M --> N
    M --> P
    M --> Q[Client Review / Approve]
```

---

## Feature-to-Page Mapping

| Feature                | Page                     | Component / API                       |
| ---------------------- | ------------------------ | ------------------------------------- |
| Projects list          | Projects (`/projects`)   | `ProjectList` / `get_projects`        |
| Create/edit project    | Project form             | `ProjectForm` / `create_project`, `update_project` |
| Project progress       | Project details          | `ProgressBar` / `get_project`         |
| Deliverables           | Deliverable lists/detail | `DeliverableList`, `DeliverableDetail` |
| Create deliverable     | Deliverable list modal   | `create_deliverable`                  |
| Deliverable workflow   | Deliverable detail       | `update_deliverable_status`           |
| Tasks                  | Task list/detail         | `TaskList`, `TaskDetail`              |
| Create/edit task       | Task modals              | `create_task`, `update_task`          |
| Task status            | Task detail              | `update_task_status`                  |
| Time logging           | Task detail              | `Time Logs` panel / `create_time_log` |
| Comments               | Project/deliverable/task | `CommentSection`                      |
| Attachments            | Project/deliverable/task | `FileUpload` / `project_management.api.file.*` |
| Gantt chart            | Gantt chart              | `GanttChart` / `get_gantt_tasks`      |
| Reports                | Reports page             | `Reports` / `get_progress_report`     |
| Notifications          | Topbar                   | `get_notifications`                   |
| Member focus           | Member dashboard/task    | `toggle_today_focus`                  |
| Client review          | Client deliverable       | `ClientDeliverableView`               |
| Vendor delivery        | Vendor deliverable       | `submit_deliverable`                  |
| Member invite          | Client project           | `invite_project_member`               |

---

## Technologies Used

```text
Vue 3
Vite 5
Frappe UI (1.0.0-beta.29)
Vue Router 4
Feather Icons
Tailwind CSS 3 (Frappe UI preset)
PostCSS / Autoprefixer
Frappe Framework (backend, via whitelisted APIs)
```

---

## Design System / UI

The UI follows the **Frappe UI design system**:

- Frappe UI components (`Button`, `Badge`, `Avatar`, `Dialog`, `Input`, `Select`, `Autocomplete`, `Toast`, `Dropdown`, `Tooltip`)
- Frappe UI `List` views with styled list rows and cells
- `Sidebar`, `SidebarItem`, `SidebarLabel` for navigation
- Frappe UI Tailwind preset for spacing/colour tokens (`surface-*`, `ink-*`, `outline-*`)
- Status badges coloured via `src/utils/statusColors.js`
- Progress indicators via the custom `ProgressBar` component
- Card-based layouts (`bg-white rounded-xl border border-gray-200`) for dashboards and detail pages
- Modals for create/edit forms and confirmations
- Feather icons alongside Frappe UI's Lucide-style icons

---

## Responsive Design

The application is primarily a desktop workspace, but uses responsive Tailwind classes:

- **Desktop** — full multi-column grids, sidebars, and wide list views
- **Tablet / mobile** — responsive grids collapse (`grid-cols-1`, `md:grid-cols-*`, `lg:grid-cols-3`), and the sidebar is collapsible
- The vendor dashboard hides secondary columns on small screens (`max-sm:hidden`) and overrides the list grid for mobile (`max-sm:[--list-columns:...]`)
- Utility classes such as `sm:w-72`, `sm:w-auto`, `grid-cols-2 md:grid-cols-4` adapt forms and stat cards to smaller viewports

---

## Error Handling / Loading States

- **Loading** — `LoadingIndicator` shown while API requests are in flight on list and detail pages
- **Empty states** — the reusable `EmptyState` component with icon + message, plus inline "No projects / tasks / deliverables" text
- **API failures** — fetch errors are caught and the page falls back to an empty array (and `console.error`), preventing crashes
- **Delete confirmation** — destructive actions use a `Dialog` with an explicit confirm step
- **Form validation** — required fields disable submit buttons (e.g. task/deliverable title, invite email) and inline error messages are shown (e.g. duplicate members, password mismatch on registration)
- **Skeleton loaders** — the vendor dashboard uses `Skeleton` placeholders while loading
- **Notifications** — success/error toasts via `ToastProvider`

---

## Future Improvements

> These are **possible future enhancements**, not currently implemented features.

- Add automated end-to-end tests for routing and role-based access
- Add dark mode support
- Introduce a global search across projects, deliverables, and tasks
- Add drag-and-drop task prioritisation (kanban-style boards)
- Add CSV/PDF export for reports
- Add internationalisation (i18n) for multi-language support

---

## Contribution

1. Fork and clone the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes to the frontend source.
4. Test the application (`npm run dev` with a running backend, or `npm run build`).
5. Commit and push your branch, then open a pull request describing your change.

---

## License

The frontend repository itself does not yet declare a license. The parent `project_management` Frappe app includes an `MIT License` in `license.txt` at the app root.

```text
License information has not been specified yet.
```
