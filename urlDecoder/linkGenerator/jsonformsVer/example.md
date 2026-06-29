---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
language_info:
  name: python
  pygments_lexer: ipython3
  nbconvert_exporter: python
---

# jsonforms

## simple with JSON

```{jsonform}
{
  "type": "object",
  "properties": {
    "name": { "type": "string", "title": "Your name" },
    "age":  { "type": "integer", "title": "Age" }
  }
}
```

## same with YAML

```{jsonform}
type: object
properties:
  name:
    type: string
    title: Your name
  age:
    type: integer
    title: Age
```

## strings, formats and descriptions

`format` switches the input widget; `description` shows helper text under the field.

```{jsonform}
type: object
properties:
  fullName:
    type: string
    title: Full name
    description: As it appears on your ID
  email:
    type: string
    title: Email
    format: email
  website:
    type: string
    title: Website
    format: uri
```

## numbers with constraints

`integer` vs `number`, plus `minimum` / `maximum` bounds (used for validation).

```{jsonform}
type: object
properties:
  quantity:
    type: integer
    title: Quantity
    minimum: 1
    maximum: 10
  price:
    type: number
    title: Unit price
    minimum: 0
```

## booleans

`boolean` renders as a checkbox.

```{jsonform}
type: object
properties:
  subscribe:
    type: boolean
    title: Subscribe to the newsletter
  acceptTerms:
    type: boolean
    title: I accept the terms and conditions
```

## dates and times

Driven by the `format` keyword on a `string`.

```{jsonform}
type: object
properties:
  birthday:
    type: string
    title: Date of birth
    format: date
  appointment:
    type: string
    title: Appointment
    format: date-time
  reminder:
    type: string
    title: Reminder time
    format: time
```

## single choice (dropdown)

An `enum` on a `string` renders as a select.

```{jsonform}
type: object
properties:
  color:
    type: string
    title: Favorite color
    enum:
      - red
      - green
      - blue
      - other
```

## multiple choice (checkboxes)

An `array` of `enum` values with `uniqueItems` renders as a set of checkboxes.

```{jsonform}
type: object
properties:
  toppings:
    type: array
    title: Pizza toppings
    uniqueItems: true
    items:
      type: string
      enum:
        - cheese
        - mushrooms
        - olives
        - pepperoni
        - onions
```

## required fields and validation

Fields listed in `required` must be filled; constraints like `minLength` and
`pattern` are validated live, and the Submit button stays disabled until the
form is valid.

```{jsonform}
type: object
required:
  - username
  - age
properties:
  username:
    type: string
    title: Username
    minLength: 3
    description: At least 3 characters
  age:
    type: integer
    title: Age
    minimum: 18
    description: Must be 18 or older
  zip:
    type: string
    title: ZIP code
    pattern: "^[0-9]{5}$"
    description: Five digits
```

## a list of items

An `array` of `object` produces an add/remove list of sub-forms.

```{jsonform}
type: object
properties:
  contacts:
    type: array
    title: Contacts
    items:
      type: object
      properties:
        name:
          type: string
          title: Name
        phone:
          type: string
          title: Phone
```

## custom UI Schema

So far the body has been a bare JSON Schema, and JSONForms auto-generates the
layout (every field stacked vertically). To control the layout, provide a
**UI Schema** alongside the schema, using the `Schema:` / `UISchema:` / `Data:`
form. The simplest case where it makes a visible difference: placing two fields
side by side with a `HorizontalLayout`.

```{jsonform}
Schema:
  type: object
  properties:
    firstName:
      type: string
      title: First name
    lastName:
      type: string
      title: Last name
UISchema:
  type: HorizontalLayout
  elements:
    - type: Control
      scope: "#/properties/firstName"
    - type: Control
      scope: "#/properties/lastName"
```

## nested objects

Nested `object` properties are **not** expanded by the auto-generated layout —
with a schema only, the nested fields simply don't show up. Supplying a UI Schema
that points at the nested scopes makes them render — here grouped in a box with
`Group`, and pre-filled via `Data:`.

```{jsonform}
Schema:
  type: object
  properties:
    name:
      type: string
      title: Name
    address:
      type: object
      properties:
        street:
          type: string
          title: Street
        city:
          type: string
          title: City
        country:
          type: string
          title: Country
          enum: [France, Germany, Spain, Other]
UISchema:
  type: VerticalLayout
  elements:
    - type: Control
      scope: "#/properties/name"
    - type: Group
      label: Address
      elements:
        - type: Control
          scope: "#/properties/address/properties/street"
        - type: Control
          scope: "#/properties/address/properties/city"
        - type: Control
          scope: "#/properties/address/properties/country"
Data:
  address:
    country: France
```

# styling

## theme variables (site-wide)

The form's look is exposed through CSS custom properties (`--jsonform-accent`,
`--jsonform-radius`, `--jsonform-border`, ...). Because inherited properties
cross the shadow-DOM boundary, a site can override them with ordinary CSS. Here
`_static/style_local.css` (loaded from `myst.yml`) sets a green accent and
rounder corners — which applies to **every** form on this page (notice all the
Submit buttons are green). No per-directive option is needed.

```{jsonform}
type: object
properties:
  name:
    type: string
    title: Name
  role:
    type: string
    title: Role
    enum: [student, teacher]
```

## inline CSS

The `Style:` chunk can carry verbatim CSS rules, injected into this form only
(after the base stylesheet, so they win). Here: thick red borders and red
labels.

```{jsonform}
Schema:
  type: object
  properties:
    name:
      type: string
      title: Name
    role:
      type: string
      title: Role
      enum: [student, teacher]
Style: |
  .control input,
  .control select {
    border: 3px solid #c0392b;
  }
  .control > label { color: #c0392b; }
```

## external CSS file

A `Style:` value that is a path or URL ending in `.css` is treated as a
reference: mystmd stages the file and links it inside this form's shadow root.
Here `_static/style_forms.css` (purple, dashed borders, small-caps labels).

```{jsonform}
Schema:
  type: object
  properties:
    name:
      type: string
      title: Name
    role:
      type: string
      title: Role
      enum: [student, teacher]
Style: _static/style_forms.css
```

# a survey, in one form

A single `{jsonform}` can mimic a multi-section Google Form. The `UISchema`
arranges fields into titled `Group` sections, with a `HorizontalLayout` for the
name/email row and `options: {multi: true}` for the multi-line comment. The three
language picks share one list of 12 options via a `definitions` entry referenced
with `$ref` (so the list is written once). Choosing the same language twice is
*not* prevented — JSON Schema can't express that across separate fields.

```{jsonform}
Schema:
  type: object
  definitions:
    language:
      type: string
      enum:
        - Python
        - JavaScript
        - TypeScript
        - Rust
        - Go
        - C
        - C++
        - Java
        - Julia
        - R
        - Haskell
        - Ruby
  properties:
    name: {type: string}
    email:
      type: string
      format: email
      pattern: '^[^@\s]+@etu\.minesparis\.psl\.eu$'
      description: Must end in @etu.minesparis.psl.eu
      errorMessage: Please use your @etu.minesparis.psl.eu address
    choice1: {$ref: "#/definitions/language"}
    choice2: {$ref: "#/definitions/language"}
    choice3: {$ref: "#/definitions/language"}
    comment: {type: string}
  required: [name, email, choice1, choice2, choice3]
UISchema:
  type: VerticalLayout
  elements:
    - type: Group
      label: About you
      elements:
        - type: HorizontalLayout
          elements:
            - {type: Control, scope: "#/properties/name", label: Name}
            - {type: Control, scope: "#/properties/email", label: Email}
    - type: Group
      label: Your top three languages
      elements:
        - {type: Control, scope: "#/properties/choice1", label: First choice}
        - {type: Control, scope: "#/properties/choice2", label: Second choice}
        - {type: Control, scope: "#/properties/choice3", label: Third choice}
    - type: Group
      label: Anything else?
      elements:
        - type: Control
          scope: "#/properties/comment"
          label: Comments
          options:
            multi: true
Data:
  email: "@etu.minesparis.psl.eu"
```