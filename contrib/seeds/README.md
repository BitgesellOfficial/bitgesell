### Seeds ###

Utility to generate the seeds.txt list that is compiled into the client
(see [src/chainparamsseeds.h](/src/chainparamsseeds.h) and other utilities in [contrib/seeds](/contrib/seeds)).

The seeds compiled into the release are created from sipa's DNS seed data, like this:

    curl https://bitcoin.sipa.be/seeds.txt.gz | gzip -dc > seeds_main.txt
    python3 makeseeds.py < seeds_main.txt > nodes_main.txt
    cat nodes_main_manual.txt >> nodes_main.txt
    python3 generate-seeds.py . > ../../src/chainparamsseeds.h

## Dependencies

Ubuntu, Debian:

    sudo apt-get install python3-dnspython

and/or for other operating systems:

    pip install dnspython

See https://dnspython.readthedocs.io/en/latest/installation.html for more information.
