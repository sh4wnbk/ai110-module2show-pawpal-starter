# PawPal+ Project Reflection

## 1. System Design

- Core action 1: A user can create a pet-owner profile and add one or more
  pets with details like name, species, age, and care preferences.

- Core action 2: A user can schedule walks or care activities by selecting a
  date, time, and pet.

- Core action 3: A user can view today's tasks in one place to see what needs to be done and when.

**a. Initial design**

The final UML design uses four classes that work together to support daily pet care planning. Task represents a single care event and stores what needs to be done, when it happens, how long it takes, how urgent it is, whether it repeats, and whether it is complete. It can mark itself complete and clone itself for a new date to support recurring events. Pet stores details like species, age, energy level, medical notes, and care preferences, and it owns a list of tasks so it can identify which tasks are still pending. Owner keeps a list of pets and can collect all tasks across all pets into one place for scheduling. Scheduler is created with an Owner and uses that relationship to access task data at runtime, sort tasks by time, detect conflicts, generate recurring tasks for a target date, show a daily plan, and explain the reasoning in plain language.

**b. Design changes**

The design changed in a few important ways during implementation to reduce ambiguity and avoid duplicated state. The Scheduler originally had its own tasks attribute in the UML, but that was removed because Scheduler can get tasks from Owner at runtime through get_all_tasks(); keeping a second task list would create two sources of truth that could drift out of sync. Literal type aliases for Priority, Frequency, and EnergyLevel were added so type checkers can catch invalid values like "urgent" or "very high" earlier, before execution. Method stubs use raise NotImplementedError instead of pass so unfinished behavior fails loudly with a clear message instead of silently returning None. Scheduler was also given an owner attribute in __init__ so methods can access shared task data without requiring Owner as an argument on every call. Finally, handle_recurring_tasks and show_daily_plan were updated to accept target_date, because relying on an implicit "today" would make behavior harder to test and less flexible.

Also, during the review process, Copilot was asked to review the skeleton twice. The first pass caught the missing target_date parameters, which was a useful find. A second review was run after the fix to see whether Copilot would acknowledge the change or repeat itself — it repeated the same findings and only mentioned the fix briefly at the end. This suggests AI review tools are most useful when something has actually changed; reviewing an unchanged file mostly regurgitates the same output again.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: time, priority, and frequency. Time is the primary ordering constraint — tasks are sorted chronologically so the day flows in a logical sequence. Priority is used as a tiebreaker when two tasks share the same start time, ensuring high-priority tasks appear first. Frequency determines whether a task appears on a given date at all — once tasks are date-matched, daily tasks always appear, and weekly tasks appear only on the matching weekday. These three constraints were chosen because they map directly to the core actions a pet owner actually cares about: what needs to happen, how urgent it is, and how often it recurs.

**b. Tradeoffs**

The conflict detector checks adjacent tasks after sorting by time, which means it only catches overlaps between consecutive tasks. If three tasks overlap simultaneously, it reports the first two pairs but may miss non-adjacent combinations. This tradeoff keeps the logic simple and linear (O(n)) but would need revision if the app needed to handle dense, multi-pet schedules. The method also uses timedelta arithmetic rather than timestamp math, which improves readability at no performance cost.

---

## 3. AI Collaboration

**a. How you used AI**

I used Copilot differently in each phase instead of treating it as one continuous assistant conversation. In Phase 1, I used it mainly for design and UML iteration, including a diagram review in Step 5 where it caught the duplicate tasks attribute on Scheduler without being prompted to look for that specific issue. In Phase 2, I used Agent mode to implement method stubs; it read the file, checked the README for project context, implemented all stubs, and then caught and fixed three of its own errors before finishing. In Phase 4, I used AI mostly for algorithm-level help around sorting, filtering, recurrence, and conflict logic. Keeping those phases in separate chat sessions helped keep each context clean so earlier design discussion did not leak into implementation prompts, and implementation chatter did not distract from algorithm work.

I also used the Generate documentation smart action to add docstrings quickly and cleanly without touching business logic. That was one of the most efficient uses of AI in the project because it improved clarity and maintainability with low risk of behavior changes.

**b. Judgment and verification**

Using AI well required active judgment instead of automatic acceptance. In Phase 1, when Copilot was asked to generate classes without UML context, it produced eight classes, including ScheduleItem, DailyPlan, TaskRepository, and PawPalSystem. I rejected that proposal because it introduced unnecessary abstraction for this scope and kept the design to four classes. In Phase 4, I also modified a generated check_conflicts approach that used raw timestamp math and manual indexing, replacing it with timedelta arithmetic and zip(tasks, tasks[1:]) for clearer and safer overlap checks.

The biggest lesson from leading the architecture was that AI outputs can look plausible even when they are not the best design choice. The most valuable skill was deciding when to reject a suggestion, when to modify it, and when to accept it as-is. I also learned that running a second review pass on an unchanged file mostly reproduces the same findings, so AI review is most useful after real changes. Ultimately, design coherence remains the developer's responsibility: AI can accelerate implementation details, but it cannot own the system architecture.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers eight behaviors: marking a task complete and verifying its status changes, adding a task to a pet and verifying the count increases, filtering pending tasks after completion, cloning a task for a new date, detecting overlapping tasks, sorting tasks into chronological order, generating the next occurrence after completing a daily recurring task, and flagging a conflict between two overlapping tasks. These tests matter because they verify the core scheduling behaviors the app depends on — if any of these fail, the daily plan, conflict warnings, or recurring task logic would produce incorrect results.

**b. Confidence**

The system handles normal use reliably across all tested scenarios. The confidence rating is 4 out of 5 because edge cases remain untested: an owner with no pets, a pet with no tasks, a weekly task being correctly excluded on non-matching weekdays, and conflict behavior when tasks from different pets overlap simultaneously. These gaps do not affect typical use but represent scenarios where the system's behavior is assumed rather than verified.

---

## 5. Reflection

**a. What went well**

The clearest success was the design decision to keep the system to four classes. That constraint forced every method to have a clear home and prevented the kind of over-engineering that Copilot defaulted to when given no design guidance. The CLI-first workflow in Phase 2 also worked well — verifying logic in the terminal before connecting the UI meant that by the time app.py was wired up, the backend was already known to work correctly.

**b. What you would improve**

The main thing to redesign would be how pet context is preserved when the Scheduler flattens tasks. Currently, once tasks are collected into a single list via get_all_tasks(), the connection to which pet each task belongs is lost. A cleaner approach would have get_all_tasks() return (pet, task) pairs, so methods like explain_plan() could reference the pet by name when describing the schedule. This was flagged during the Phase 2 review but deferred as a known open question rather than a skeleton concern.

**c. Key takeaway**

The most important thing learned was that being the lead architect means owning every decision, including the ones AI makes on your behalf. AI tools generate output quickly and confidently, but confidence is not the same as correctness, and speed is not the same as good design. The skill is not in prompting AI to produce something — it is in evaluating what it produces, knowing what to keep, what to change, and what to reject entirely.

---

## 6. Multi-Model Prompt Comparison

To evaluate how different AI models approach the same scheduling problem, I asked three tools to implement the recurring task rescheduling logic — specifically, the behavior where marking a daily or weekly task complete returns the next scheduled instance.

**GitHub Copilot** generated a working implementation but included dead code in the daily frequency branch — it wrote an initial approach using date.replace(), then overwrote it with the correct timedelta approach without removing the first attempt. It also placed timedelta imports inside the method body rather than at the top of the file. The logic was correct 
but the code required cleanup before committing.

**Claude** produced a cleaner version with timedelta imported at the top level and no dead code, but initially used pass stubs instead of 
raise NotImplementedError, which would have failed silently rather than loudly. It also added the owner: Owner attribute to Scheduler that Copilot missed when generating the skeleton without UML context.

**Gemini** (used in Phase 1 for the initial class blueprint) produced a reasonable structure but was missing duration_minutes and priority from the Task class entirely, requiring manual correction before the design could proceed.

**Takeaway:** Copilot was the most effective tool for in-editor, file-aware tasks — it could read the project files and generate 
contextually accurate code. Claude was more useful for design decisions, evaluation, and catching logical gaps that required reasoning across the whole system. Gemini was useful for initial brainstorming but required the most correction. No single tool was sufficient on its own — the best results came from using each where it was strongest and critically evaluating every output before accepting it.
