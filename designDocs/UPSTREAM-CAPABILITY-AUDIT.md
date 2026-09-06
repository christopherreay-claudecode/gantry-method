# The upstream-capability audit — when a base gains a capability after the fork

*Companion to METHOD-shape.md. Written from the case of 2026-09-06: svelteKitOnSupabase
(the base) gained a working, provable mail world; cubeOnSKOS (forked at 7f2e955, ~40
migrations earlier) had been designed throughout on the accidental assumption that no
mail existed. The question was not "how do we bolt mail on" but "what did the absence
bend, and what do we un-bend".*

## 1. The situation has a shape

A fork inherits the base's constraints and its world. When the base later gains a
capability, the fork has meanwhile made decisions *around* the absence. Those decisions
are not marked; they look like design. Three kinds hide together:

1. **symptoms** — things that would have been designed differently (a password typed on an
   invite page because no message could carry a link);
2. **compensating mechanisms** — machinery that exists only to stand in for the capability
   (a UI step that shows a link for the human to carry; "the inviter may approve" because
   only the inviter knows whom they handed the link to);
3. **invariants that merely look like symptoms** — things that must NOT change (a
   participant key shown once and never stored is not a no-mail symptom; there is no
   address to send it to, by constraint).

The audit exists to separate the three before anyone files a workorder.

## 2. Name the capability precisely: world or feature?

Say exactly what the base now has. Mail "working" turned out to mean: a transport that is
proven locally (a catcher with a measured accept counter), the auth system's templates as
versioned repo artefacts pushed by config, a declared site root every link is built from,
a local sink the app tier can also reach, and a per-tier overlay for the real provider.
It did NOT mean an app-level sender, or passwordless login, or custom templates. Filing
against "email" instead of that list produces workorders for things the base does not
have and misses the ones it does.

## 3. Grep for the absence fingerprint

The absence leaves text. Search issues, specs, journeys, contract, migrations, commit
messages and code for:

- **apologising copy** — "if email is set up for this site", "no email is sent by this
  site", "send this to them yourself", "out of scope (later): the actual send";
- **hand-carried artefacts** — a token returned to the browser and displayed; a step whose
  only purpose is copy-to-clipboard; an address field that is prefilled *but editable*;
- **human-memory provenance** — approval arms for "whoever invited them"; a name asked at
  the moment of joining because nothing else is known;
- **page-only notices** for conditions a person is not looking at (a dead sink, a queue
  running down, "results are not published yet" as pull);
- **rate limits whose stated threat could not occur** ("mail flood → relay abuse" on a
  door that sends nothing) and doors left unthrottled because tokens were scarce;
- **dead branches** — a recovery link with no page behind it; a "confirm your email"
  sentence in a flow where confirmations are off;
- **deployment docs** where the only address is the certificate contact.

## 4. Classify every hit, with its constraint

For each hit: the decision (path:line or issue), the evidence it was shaped by the
absence (a quote), the constraint it serves, and the plausible alternative. Then sort it
into §1's three kinds. The constraint column is what stops a symptom from being "fixed"
into a violation: in the cube case, everything participant-facing sorted as *invariant*
under constraint 19 (no re-identification) even where it looked like a symptom.

## 5. Map onto the base's propagation stance

The base states how a capability reaches existing forks (config parity, a harness to
port, a hand-adoption list, or "existing apps adopt by hand"). Write the hand-adoption
list explicitly: config sections, template directories, overlay files, exit-test scripts,
posture specs. This is the *foundation* layer; nothing else lands before it.

## 6. File in three layers, text first

1. **Foundation** — port the world (config, harness, seam declaration). One workorder each.
2. **Retirement** — remove compensating mechanisms, one workorder each, each naming the
   mechanism it retires and the test that proves it gone (the "send it yourself" step; the
   editable address; the password born on the invite page).
3. **Amendment** — where a constraint or a journey *encoded* the absence (a principal
   defined as "password sign-in"), file the human-gated amendment before the workorder.

Every layer changes text before code: the journey file, the contract entry, the spec.
The mirror tests then say what code must catch up. Symptoms that were decisions with
their own merit (an inviter-may-approve arm is also a convenience) get a `?` for the
owner, not a silent retirement.

## 7. The one thing to remember

**An absence is a design input.** When it ends, audit what it shaped before adding what
it enables; otherwise the compensations survive beside the capability and the system
carries both.
