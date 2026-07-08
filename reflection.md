# PawPal+ Project Reflection

## 1. System Design

Three core actions a user should be able to perform are to enter owner/pet info, add and edit tasks to do, and generate a plan depending on constraints and priorities. 

**a. Initial design**

The classes I chose were Owner, Pet, Task, ScheduleItem, Owner, and Scheduler. The responsibilities of Owner are having an id, name, and email, a list of pets, and adding and removing pets. The responsibilities of Pet are to hold data about it (id, name, species, age), get special edge cases with special_notes, and have a way to modify it with update_profile. Task links itself to a specific pet using pet_id, defines the scheduling rules/constraints for the algorithm, and allows editing these configuration constraints. ScheduleTask implements Task, and binds it with a start and end time and state-changing methods (complete/skipped). Scheduler keeps track of the global constraints for the day via available_hours, creates the schedule, and fixes any conflicts.

**b. Design changes**

Yes, my design changed. One change is that Task had no direct link to Pet objects, only the pet_id string. the Scheduler would only get a list of Tasks, so it can't look up the pet's special_notes during scheduling, which could entail important medical conditions (like "don't feed after 8pm"). This is important for a pet's safety and well-being, so it was changed so that Task gets a direct Pet reference by adding it as a field on Task.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The constraints the scheduler considers are availble hours, preferred window, task duration, and no double-booking. I decided these matter most because these are the fundamental parts of creating a schedule that works well, with complexities such as preferred windows as well as priority levels.

**b. Tradeoffs**

One tradeoff my scheduler makes is that it assigns each task to the earliest available spot and moves on, never reconsidering that decision. The tradeoff of this is that a large low-priority task that was placed early can block multiple smaller high-priority tasks that come later in sorted order.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools during design brainstorming, debugging, and writing test cases. I think the most helpful were writing test cases since I'm not too familiar with how to do that with pytest, and if I was confused I could ask the AI to explain the test case to me and how it worked.

**b. Judgment and verification**

One moment I did not accept an AI suggestion as-is was when I was getting help writing one of the methods (I can't remember at the moment which one it was specifically) but when I asked it for help it gave me a really convoluted and long-way of doing the task, when I knew that there should be a simpler way of doing it.

---

## 4. Testing and Verification

**a. What you tested**

The behaviors I tested were Sorting, Recurrence, Conflict detection, Preferred window, and Deduplication. These tests were important because these behaviors were the ones that were most likely to break or create confusion. Doing the test showed that they do not break.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident at a 4 out of 5 that it works correctly. Edge cases I would test if I had more time are probably the logic of `resolve_conflicts`, I feel like that part is probably very error-prone since two tasks could overlap and have the same priority number, but the existing task would win at the moment with the current logic.

---

## 5. Reflection

**a. What went well**

I'm satisfied with how the website looks and runs.

**b. What you would improve**

I think I would work a little more on the UI and make it more fun and colorful, something cool could also be like seeing it visually like calendar daily/weekly format.

**c. Key takeaway**

One important thing I learned about designing systems on this project is how useful creating UML diagrams can be at the beginning of a project to get a sense of what needs to get done and how everything interacts, and so at the end you can see how you've improved from the start.
