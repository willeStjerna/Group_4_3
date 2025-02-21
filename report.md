# Report assignment 3

**Project Name:** piqueserver

**URL:** https://github.com/piqueserver/piqueserver

Piqueserver is an open-source and cross-platform server implementation for the game Ace of Spades. It is based on a previous software package called PySnip and aims to continue the work from that project.
Onboarding experience

# Onboarding

The project itself was rather easy to build but could be improved since the instructions on the https://docs.piqueserver.org/en/latest/contributing-developer.html didn't work since they had removed the requirements.txt file. Additionally, there are instructions in the docs folder which is also inconsistent with other documentation, also relying on the requirements.txt file. However, we found that the working solution was to follow the short instructions located in the repos README, specifying two commands to build to project. These commands simply create a virtual environment, enter the virtual environment and then install dependencies. Except for the dependencies installed from the command presented in the README, they present an additional command in the docs website which installs Cython. Cython is according to the developers important to avoid issues with Pytest. On Linux/Ubuntu, the build was completed without errors. However, the Windows build encountered a minor issue, which did not affect test execution. To run all tests we simply need to run “pytest” which executes all test files and it only takes about five seconds.

# Complexity

**Function 1 (Arvid):** 
Directory: piqueserver/corecommands/movement.py. Function name: do_move. CC according to lizard.py: 19. Manual calculated CC: 19. Verified by Marcus.

It’s a rather long function and somewhat complex. The NLOC of the function is 43, meaning it is pretty long and could benefit from being divided into smaller functions that represent the small core functionality of the larger do_move function. The complexity of 19 also suggests that it could be divided into smaller functions to reduce the CC and thus improve readability and understandability.

The function’s purpose is to move a player to a sector or to coordinates. Only an admin or another player with permission can move another player. The movement can be done silently or not silently (essentially recording the move in a message or not).

There are no try/except statements in the function. Errors are instead handled by using if/else statements and by raising an error in the else statement if any unexpected input is provided.

Not really that clear. The function is missing a docstring with information about the function and not all functionality is commented. The reader is left to interpret much of the code themselves which makes the understandability very poor for the function.

**Function 2 (Marcus):** 
The second function is on_block_destroy, in the directory piqueserver/player.py. When calculating by hand, I got the result CC = 17. This is the same result that both André and Lizard got as well. 

The function is complex, but not very long. It has a relatively high CC, but only 26 LOC. It depends completely on the structure and purpose of the function. The high complexity is because the function checks a lot of different conditions and thus has many conditional (if, elif, else) statements. Other functions of the same length that for example performs some calculation might have a very low CC value. The purpose is to check several conditions for destroying a game object which is the reason for the high CC. If the exception is counted as another possible branch the CC increases. The on_block_destroy function has no exceptions, so they do not need to be included in the tool.

There is no documentation included for the function, neither in the online documentation nor in the form of comments in the source code. As such it takes some time to understand the function and how different parameter values affect the branches covered.

**Function 3 (William):** 
For the function grenade_exploded in pydespades/player.py I got CC number to be 20 when calculating by hand which is the same as the tool Lizard. Arvid did also get 20. This function is not very long in terms of LOC, but could be argued to be long in terms of what it does. It has a lot of conditions where some are nested. The function handles the effects of a grenade explosion in a game. It verifies the grenade's validity by checking if the player who threw it is still valid, applies damage to nearby players based on the explosion's position, handles different outcomes depending on whether the explosion kills a player, destroys nearby blocks in the game world while tracking how many were removed, and updates the game state by broadcasting changes to other players. The high cyclomatic complexity is directly related to these responsibilities because the function checks many different conditions, including player and team validation, damage calculation, and hit verification. It modifies multiple game components such as player health, block destruction, and game updates. Additionally, it contains nested loops for handling multiple players and checking block destruction. This suggests that the function could be broken down into smaller, more focused helper functions to improve readability and maintainability. There is no use of exceptions in the function. There is also no documentation for this function.

**Function 4: (André)** | Function name: on_block_line_recieved | Located in: ./pyspades/player.py
NLOC: Lizard: 52, Manual counting (excluding comments): 52 
CCN: Lizard: 19, Manual counting using 1 + 1 per if/for/and/or: 19 Verified by William.
The results seem reliable because the tool gave the same results as both of us counting.
The NLOC is much higher than CCN and that is mainly because many if statements exists that could have been a single line so it inflates the NLOC a bit, 
The function has a high CCN because it has many if statements that makes the function return early if something is wrong.
No exceptions were used in this function. Lizard does take into account each “except:” so each one would add +1 to CCN.
There is some documentation of the function in the form of comments that explain why it returns early. But it’s not comprehensive. Also, it does not document what happens if the function succeeds and runs all the way to the end.

# Refactoring

**Function 1:**
Refactoring plan includes some fixes that I think are the most urgent to address:
- Move validation of privileges to separate functions (for example admin validation).
- Create a separate movement logic function for better readability.
- Create a separate function to handle the move arguments for better readability.

By carrying out this refactoring plan, the readability and understandability of the function will improve. The total CC of the function will also be lower as much of the if/else statements will be outsourced to other smaller functions. The estimated impact of refactoring will be 4 for do_move as mostly all of the conditional statements can be moved to separate functions. There would not be any major drawbacks to performing this refactoring, however, the running time of the function do_move could increase as it calls many other smaller functions, but should again not be of any concern.

**Function 2:**
The function can be refactored, which would lower the complexity. The function takes the current “mode” as a parameter, decided by the current state of the game, which in turn impacts which parts of the code will be executed. The code for each of these modes could be converted into their separate functions so that all logic for that specific mode is contained in a separate block of code. However lowering it to more than this would not be very possible, as the purpose of the function is to check these conditions and thus a lot of branches must be included. 

Refactoring according to the description above would both lower the CC and also improve readability, as each separate mode case is contained in separate functions. However, it potentially also leads to other drawbacks. Depending on how many times blocks are destroyed in the game, this refactoring could lead to a substantial increase in the number of function calls the system performs. Since function calls are more computationally heavy in Python compared to other languages, this refactoring might not be worth the drawbacks.

**Function 3:**

The complexity of grenade_exploded is quite high due to multiple responsibilities being handled in a single function. It checks conditions for ignoring the explosion, processes damage for players, verifies hit validity, updates player health, destroys blocks, and broadcasts changes—all within one block of code. This results in deep nesting, multiple conditional checks, and a mix of concerns that could be better organized.

To reduce complexity, the function can be split into smaller, more focused helper methods. The first step would be to extract the validation checks into a separate function, such as is_valid_explosion, which would determine whether the grenade should be processed at all. Next, handling player damage could be separated into a method like apply_grenade_damage, which would iterate over affected players and apply damage accordingly. The logic for handling block destruction could also be moved into process_block_destruction, making it clearer and easier to modify. By refactoring in this way, the main grenade_exploded function would act as a high-level controller, calling these helper methods in sequence rather than performing all operations itself. 

**Function 4:**
I would not say the function is complex to a human reading it. The NCC is a bit misleading here. It consists of many but shallow ifs that don't need untangling. I can see 3 areas that could do with improvements:
There is one part about detecting hacking that should be moved to its own function, as it is not relevant to this function. This would shorten it by 10 lines, reduce its CC by 4, and remove 4 branches. 
One could clump the tests around points into one function and separate that from this function. That would reduce it by 10 branches. But It could also hurt readability by having it in another location.
There could be more documentation around the checks and why they have to pass. I would add comments explaining why each if statement must fail for the function to reach its end.

# Coverage
We all used Coverage.py as the coverage tool. The tool is well-documented and is easy to get started with. The more tricky part was to be able to see the coverage of a specific function which required us to create an HTML file and a local Python server (from what we could find). But overall, it was not too difficult to set up and use. Furthermore, it was already integrated into the build environment so a simple “pip install coverage” was enough to be able to run coverage on the repo.

**Our coverage tool:**
Coverage improvement (comparing the results from our manual tools to the results from using Coverage.py).

Coverage (%)
Arvid
Marcus
William
André
Coverage.py
58
65
51
58
Manual Tool
44
36,36
33
46


Arvid’s manual tool on branch: https://github.com/willeStjerna/Group_4_3/tree/arvid

William’s manual tool on branch: https://github.com/willeStjerna/Group_4_3/tree/william 

Marcus’s manual tool on branch: https://github.com/willeStjerna/Group_4_3/tree/marcus 

André’s manual tool on branch: https://github.com/willeStjerna/Group_4_3/tree/andre

**Function 1:**
My measurement does not account for ternary operations. The program was however modified to account for this by splitting up ternary operations to multiple lines. The tool uses a Python dictionary which tracks certain branches of a function (which makes it rigid and not flexible to other functions, but more easily readable).
Limitations are for example: does not track sequence (interprets every branch as independent), inefficient use of storage (using Python dictionary), if we add more code to function the dictionary has to be updated accordingly with new entries (low flexibility when considering new code/other functions).
There were no tests provided for the do_move function, so the coverage was 0% at first. I added two tests and the results from Coverage.py: approximately 58% of branches are covered by tests, and the manual testing also reports approximately 44%. This can be mostly explained by the fact that Coverage.py includes partial coverage in its reporting, that is including branches that were partially covered but not completely covered (this is not accounted for in the manual testing).

**Function 2:**
My coverage tool is specifically tailored to the on_block_destroy function and tracks its individual branches through a Python dict (branches being defined as if and while statements). My measurement tool does not take ternary operations into account, however as my function does not include any such operations it does not impact the coverage result. Similarly, there are no exceptions included in my function.
As I mentioned, my tool is specifically tailored to the on_block_destroy function. This means it cannot be used to measure the coverage of other functions without modifying, which is a big limitation. The fact that it does not take ternary operations or exceptions into consideration is also a big limitation, which would need to be fixed to expand it into a fully functional universal tool. It also uses Python dict as the data structure, which is not the most efficient in terms of memory.
The results of my coverage tool varied quite a bit from coverage.py. After adding the two tests, my tool measured 36,36% coverage while coverage.py measured 65% coverage. I suspect that this is because coverage.py measures the lines of codes executed, while my tool measures the number of individually identified branches that have been run. This has the potential to result in vastly different values, as some branches might contain more code than others.

**Function 3:**
The coverage measurement provides a structured way to track whether specific branches in the function have been executed. By manually instrumenting each conditional statement with unique branch IDs, the tool ensures that every decision point in the function is explicitly marked as covered or not covered. This makes it possible to evaluate branch execution beyond simple line coverage. However, the current implementation does not account for ternary operators, which function as inline conditionals in Python. If a condition is written as value = x if condition else y, the tool does not distinguish whether the if or else 
One major limitation of the tool is that it requires manual instrumentation. Each conditional branch must be assigned a unique identifier, meaning that if the function is modified by adding, removing, or altering conditionals, the branch IDs must be updated manually. This makes the tool inefficient for large-scale or frequently changing codebases. Additionally, it does not track implicit branches caused by logical conditions (and / or). If an or condition is met early, the second part is never evaluated, but the tool does not record which part of the condition was responsible for execution flow.
Since there were no tests for this function, coverage.py gave 0 %. But in order to test my implementation of branch coverage, I created a simple test for the function so it would go through the whole function and not return early. This test gave 33 % coverage according to my measurement but according to coverage.py, it was 51 %.  In the manual instrumentation, each decision point (if, else) was treated as a single branch, including compound conditions like x < 0 or x > 512 as one branch. However, coverage.py breaks down compound conditions into multiple branches, treating each sub-condition (x < 0, x > 512) as a separate branch. Additionally, coverage.py tracks implicit branches, such as short-circuit evaluations and loops, which were not explicitly implemented in the manual approach. This means coverage.py counts more branches overall, leading to a higher total branch count and a different coverage percentage.

**Function 4:**
This function did not have any tests, so the tool coverage.py showed 0%. So to have something to compare to I therefore created one test which when through a long path in the function and that test covered 58% of lines according to the tool.

My manual implementation got 14/30 ≈ 46% branches. As it is manually written, I am quite sure it is correct. However, I am unsure if one would count going into a for-loop or not as 2 separate branches. Also, and/ors were not covered. There were no ternary operator or exceptions in this function, so they were not tested. 
It is complete manually written, so one would have to add lines to each instance a branch is created and also update the tool with the correct branches.
It is not entirely consistent. It could be that coverage.py does not count going into a for loop or not as 2 different branches.

# Coverage improvement
Report of old coverage: 

https://github.com/willeStjerna/Group_4_3/blob/master/coverage_report_old.pdf 

Report of new coverage: [link]

**Function1:**

No requirements were covered at first since no tests were provided in the test file. By implementing the 5 tests, all of the requirements are tested in some way but not all combinations of requirements are tested.

Test cases added:

test_move_self_sector (R1, R3, R7, R9)

test_move_self_coordinates (R1, R3, R7, R9)

test_move_other_player_without_permission (R2, R3, R6)

test_invalid_argument_count (R5)

test_silent_move (R1, R3, R4, R7, R9)

Coverage improved from 0% to 80%.

**Function 2:**

Test cases added:

test_map_info_on_block_destroy

test_on_block_destroy_grenade_indestructable

Before added tests: 0% coverage

After added tests: 65% coverage


No tests were made for the function before the assignment, and as such the coverage for the function was 0%. After the two tests, coverage.py measures the coverage to be 65%.This is likely counting the number of lines of codes processed, as the number of branches explored in these two tests is 4/11.

**Function 3:**

Test cases:

test_ignore_spectator

test_ignore_no_name

test_ignore_enemy_grenade

test_ignore_out_of_bounds

test_dead_player_skips_damage

test_normal_path_block_destroy

test_zero_damage_skips

Coverage improved from 0 % to 90 %

**Function 4:**

No requirements were tested, so the initial coverage was 0%. 

Test cases added:

test_dead_player_returns_immediately

test_no_start_position_returns_immediately

test_rapid_hack_detection

test_not_in_range_of_start_or_end_returns_immediately

test_on_block_line_recieved_good_inputs

Coverage improved from 0% to 72%.


**Total number of test cases added per member:**

Arvid: 5 (0 from beginning)

Marcus: 2 (0 from beginning)

William : 7 (0 from beginning)

Andre: 5 (0 from beginning)

# Self-assessment: Way of working
We as a group assess that we are still in the “In Place” state of way-of-working. We all have a clear understanding of who we are, what skills the team possesses, and how we communicate. We have understood our equal responsibilities in contributing roughly equal amounts because we are using a flat structure without an official leader. For this assignment, we communicated exclusively on Discord since the structure of the assignment did not require quite the same “issue”-process that the two previous assignments did. Trust has been established by seeing the effort each person has made in assignments 1,2 and now 3. This week, we feel that we fully achieved most checkboxes for the “In Place” state in the way-of-working. We also do more regular voice calls to better make sure that we are all on the same page in our work. This was mentioned in our first essence report (for assignment 1) and has improved dramatically since then.

For this week's assignment, we can not identify many improvements in our way-of-working. The task description instructed us to simply divide the work equally among the four of us, and then the responsibility for all of us to complete our respective parts was up to each person. Looking ahead, we feel like the practices that we have previously used (commits standards, issue standards etc) can of course be further worked on, but have now been standardized among us. We have improved our communication skills as a group, making sure that everyone can get answers to any questions each team member may have.

Overall we found the project to be a very positive experience. Having to onboard a large project is a very different experience from creating a project from scratch, and getting practical experience in this regard felt necessary since few courses practice it. It was also healthy to dive deeper into real documentation, as it gave a lot of insights about potential aspects we might have neglected ourselves in the past regarding documenting details of a program. Coverage also felt like an intuitive practice to consider in future projects, having gained a good understanding of it in this assignment. Understanding how to think in terms of branches was useful for identifying edge cases when writing our tests, especially for functions with less clear input that are heavily integrated into other parts of a large project. As such we all agreed it was a very informative project to have worked on.
