## Next steps to follow this proyect..

[  ] Fix the proyect structure
            -> Scalability, cleaniness etc etc
            - [ X ] Separate the database connection and make it less hardcoded and clean.
            - [  ] Watch out how not to repeat so many times the requirements.txt and Dockerfiles (integrate later when everything is set up)
            - [ X ] Change the main loops by Threads not to block the main thread and make it more efficient and scalable
            - [   ] Include Observer and handlers for notifying modules and pro printing instead of normal prints
            - [   ] Include Queues to reducer the bottleneck as with Threads, they both go together
