# PawPal+ Project Reflection

## 1. System Design

Three core actions a user should be able to perform are to enter owner/pet info, add and edit tasks to do, and generate a plan depending on constraints and priorities. 

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The classes I chose were Owner, Pet, Task, ScheduleItem, Owner, and Scheduler. The responsibilities of Owner are having an id, name, and email, a list of pets, and adding and removing pets. The responsibilities of Pet are to hold data about it (id, name, species, age), get special edge cases with special_notes, and have a way to modify it with update_profile. Task links itself to a specific pet using pet_id, defines the scheduling rules/constraints for the algorithm, and allows editing these configuration constraints. ScheduleTask implements Task, and binds it with a start and end time and state-changing methods (complete/skipped). Scheduler keeps track of the global constraints for the day via available_hours, creates the schedule, and fixes any conflicts.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
