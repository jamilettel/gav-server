# Protocol

In order for the server and the client to communicate, there should be a protocol that they both follow. This page here describes it.

All communication is to be done in the `JSON` format.

## Commands

Commands can be sent to the server. This will allow the user to interact with the genetic algorithm either to change the settings

The commands are separated into two sections, buitlin commands and server specific commands.

The builtlin commands are necessary for the functionning of the protocol and must be integrated, whereas the normal commands are useful for manipulating the data, but not necessary for the functionning of the server.

### Builtins

Builtin commands are used to create, delete and join GA sessions.

The JSON object for those commands looks like this:

```tsx

type BuiltinCommand = {
	session: string
	[key: string]: string
}

const example: BuiltinCommand = {
	"session": "join-or-create",
	"name": "session name",
}
```

Here is the complete list of builtins:

- `join-or-create`: Joins a session, creates it if it doesn’t exist
Arguments:
    - `name`: string = name of the session you want to join
    
    Returns:
    Same as `info`
    
- `leave`: Leaves current session
    
    Returns:
    
    Same as `info` 
    
- `delete`: Leaves and deletes the session
Returns:
Same as `info`
- `list`: Lists all the sessions
Returns:

```tsx

type SessionList = {
	info: 'session_list'
	sessions: string[]
}

const example: SessionList = {
	info: "session_list",
	sessions: ["Session1", "Session2"]
}
```

- `info`: Returns information on current session
Returns:

```tsx

type SessionInfo = {
	info: 'session'
	session: string | null
}

const example: SessionInfo = {
	"info": "session",
	"session": "NAME"
}
```

- `describe`: Describe the session commands that can be used. These will only be available when you join a session.
Returns:

```tsx

type SessionDescribe = {
	info: 'session_describe'
	title: string
	command_protocol: string
}

const example: SessionDescribe = {
	"info": "session_describe",
	"title": "Travelling Salesman Problem",
	"command_protocol": "generic",
}
```

### Command Protocols

Commands are a part of the protocol where you are free to implement whatever you want to implement. You can implement additional commands if you desire.

Different command protocols can be added, feel free to add or expand an existing protocol.

Here is how comments are sent:

```tsx
type Command = {
	command: string
	[key: string]: any
}

const example: Command = {
	"command": "COMMAND",
	"ARG1": "VALUE1",
	"ARG2": 42
}
```

Here are the command protocols currently present:

- [`Generic`](GENERIC.md)