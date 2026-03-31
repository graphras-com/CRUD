/**
 * Application resource configuration — the single source of truth for the frontend.
 *
 * When creating a new application from the template, modify this file to
 * define your domain entities and their fields.  The generic CRUD components
 * (CrudList, CrudCreate, CrudEdit, CrudDetail) read this config to auto-
 * generate pages for each resource.
 *
 * Field types:
 *   "text"     — single-line text input
 *   "textarea" — multi-line text area
 *   "select"   — dropdown populated from `source` resource
 *   "number"   — numeric input
 *   "code"     — rendered in <code> tags in list views
 *
 * Special field options:
 *   source        — resource name to populate a <select> (e.g. "groups")
 *   sourceLabel   — function (item, breadcrumb) => display text for select options
 *   showInList    — show this field as a column in the list view
 *   showInForm    — true | "create-only" | "edit-only" | false
 *   required      — HTML5 required attribute
 *   nullable      — if true, empty strings are sent as null
 *   rows          — textarea rows
 */

export const resources = [
  {
    name: "groups",
    label: "Groups",
    labelSingular: "Group",
    apiPath: "/groups",
    pkField: "id",
    pkType: "string",
    navOrder: 2,
    listDisplay: "table",
    searchable: false,
    fields: [
      {
        name: "id",
        label: "ID",
        type: "text",
        required: true,
        showInList: true,
        showInForm: "create-only",
        render: "code",
        placeholder: "e.g. engineering.backend",
      },
      {
        name: "label",
        label: "Label",
        type: "text",
        required: true,
        showInList: true,
        showInForm: true,
      },
      {
        name: "parent_id",
        label: "Parent",
        type: "select",
        source: "groups",
        sourceLabel: (item, breadcrumb) =>
          `${breadcrumb(item.id)} (${item.id})`,
        showInList: true,
        showInForm: true,
        nullable: true,
        emptyLabel: "None (top-level)",
        render: "code",
      },
    ],
    children: [],
  },
  {
    name: "items",
    label: "Items",
    labelSingular: "Item",
    apiPath: "/items",
    pkField: "id",
    pkType: "number",
    navOrder: 1,
    listDisplay: "detail-cards",
    searchable: true,
    searchPlaceholder: "Search items...",
    filters: [
      {
        param: "group",
        label: "Group",
        type: "select",
        source: "groups",
        emptyLabel: "All groups",
      },
    ],
    fields: [
      {
        name: "name",
        label: "Name",
        type: "text",
        required: true,
        showInList: true,
        showInForm: true,
      },
    ],
    children: [
      {
        name: "details",
        label: "Details",
        labelSingular: "Detail",
        parentFk: "item_id",
        fields: [
          {
            name: "description",
            label: "Description",
            type: "textarea",
            required: true,
            showInList: true,
            showInForm: true,
            rows: 3,
          },
          {
            name: "notes",
            label: "Notes",
            type: "textarea",
            showInList: true,
            showInForm: true,
            nullable: true,
            rows: 3,
            suffix: "(optional)",
          },
          {
            name: "group_id",
            label: "Group",
            type: "select",
            source: "groups",
            required: true,
            showInList: true,
            showInForm: true,
          },
        ],
      },
    ],
  },
];

/**
 * Application-level configuration.
 */
export const appConfig = {
  /** Application name shown in the navbar brand and Home page */
  name: "CRUD App",

  /** Short description for the Home page */
  description: "A generic CRUD application template.",

  /** Show backup/restore links in the navbar */
  hasBackup: true,

  /** Role required for restore (destructive operation) */
  backupRole: "App.Admin",

  /** Additional Home page cards (beyond auto-generated resource cards) */
  homeCards: [],
};

/**
 * Find a resource config by name.
 */
export function getResource(name) {
  return resources.find((r) => r.name === name);
}

/**
 * Get resources sorted by navOrder for navigation.
 */
export function getNavResources() {
  return [...resources].sort((a, b) => a.navOrder - b.navOrder);
}
