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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector checks adjacent tasks after sorting by time, which means it only catches overlaps between consecutive tasks. If three tasks overlap simultaneously, it reports the first two pairs but may miss non-adjacent combinations. This tradeoff keeps the logic simple and linear (O(n)) but would need revision if the app 
needed to handle dense, multi-pet schedules. The method also uses timedelta arithmetic rather than timestamp math, which improves readability at no performance cost.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

I used AI review iteratively and verified it against actual code changes instead of accepting output at face value. Copilot reviewed the skeleton twice: the first review correctly identified that target_date parameters were missing, which was helpful and led to a concrete fix. After that fix, I intentionally ran a second review to see whether it would acknowledge what changed or mostly repeat itself. It repeated findings 1 through 4 almost unchanged and only mentioned the target_date update briefly at the end. A human reviewer would usually lead with what changed and what remains open, so this reinforced that AI review is most useful when there is meaningful new context and less useful when the same file is reviewed again without substantial changes.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
