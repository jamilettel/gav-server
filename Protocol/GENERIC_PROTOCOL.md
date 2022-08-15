# Generic Protocol

## Types

Below you will find types that will be used to describe the data that the server returns to the client. They will be used in the response descriptions.

```tsx
type Setting =
    | {
          type: 'number'
          value: number
          range?: [number, number]
          min_increment?: number
      }
    | {
          type: 'string'
          value: string
          values?: string[]
      }

type Individual = {
		id: number
		chromomose: number[]
		parent1_id: number | null
		parent2_id: number | null
		fitness: number
		mutated_from: number
		before_mutation: number[] | null
		[key: string]: any
}

type GenerationStats = {
    // graph name
    [key: string]: {
        // line name & value
        [key: string]: number
    }
}

type GeneralStats = {
    Generation: string,
    [key: string]: string,
}

type Status = 'working' | 'idle'

type IndividualEncoding =
    | {
          encoding_type: 'indexes' | 'boolean'
      }
    | {
          encoding_type: 'range'
          range: [number, number]
      }

type SettingChangelog = {
		generation: number
		setting: string
		value: number | string
}
```

---

# `info`

### Arguments

None

### Returns: `InfoAllData`

```tsx
type InfoAllData = {
    info: 'all'
    data: {
        general_stats: GeneralStats
        // each element represents one generation
        all_stats: GenerationStats[]
				populations: Individual[][]
				individual_encoding: IndividualEncoding
        settings: {
            // setting name & value
            [key: string]: Setting
        }
				status: Status
				settings_changelog: SettingChangelog[]
    }
}
```

`data.generation` represents the current generation

`data.all_stats` contains a list of all the stats, one element of the list is the information for one entire generation.

`data.settings` contain the settings that can be changed, their current values, and their possible values (if applicable)

---

# `run-one-gen`

### Arguments

None

### Returns (broadcast): `InfoOneGen`

This is broadcasted to all the clients that have joined the session, even if they didn’t send the command.

```tsx
type InfoOneGen = {
    info: 'one-gen'
    data: {
        general_stats: GeneralStats
        gen_stats: GenerationStats
				population: Individual[]
    }
}
```

**Note:** `data.gen_stats` and `data.population` only applies to the current generation

---

# `run-n-gen`

### Arguments

- `generations: number` the number to run (has to be a positive integer)

### Returns (broadcast):

- `InfoOneGen` (see `run-one-gen`) for every generaiton
- `InfoStatus` (see `get-status`): once at the start (where the status is set to `working`), and once at the end (where the status is set to `idle`).

Both are broadcasted

---

# `set-setting`

### Arguments

- `settings.SETTING_NAME: number | string` where SETTING_NAME is the name of the setting and the value of the attribute si the new value for the setting

You can send multiple settings at the same time.

### Returns (broadcast)

Same as `settings` command, but as a broadcast

---

# `settings`

### Arguments

None

### Returns: `InfoSettings` & `InfoSettingsChangelog`

See `settings-changelog` for information about `InfoSettingsChangelog`

```tsx
type InfoSettings = {
	info: 'settings-update',
	settings: {
		[key:string]: Setting
	}
}

const example: InfoSettings {
	info: "settings-update",
	settings: {
		SETTING_1: {
			type: "number",
			value: 0.6,
			range: [0.0, 1.0],
			min_increment: 0.1,
		},
		SETTING_2: {
			type: "string",
			value: "hello",
			values: ["hello", "world", "test"]
		}
	}
}
```

---

# `get-status`

### Arguments

None

### Returns: `InfoStatus`

```tsx
type InfoStatus = {
		info: 'status'
		status: Status
}
```

---

# `settings-changelog`

### Arguments

None

### Returns: `InfoSettingsChangelog`

```tsx
type InfoSettingsChangelog = {
		info: 'setting-changelog'
		settings_changelog: SettingChangelog[]
}
```
