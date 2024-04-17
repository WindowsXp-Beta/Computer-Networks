/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

struct metadata {
}

struct headers {
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

      state start{
          transition accept;
      }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action forward(bit<9> egress_port){
        /* TODO 3: Update the destination port */
        standard_metadata.egress_spec = egress_port;
    }

    action random_forward(bit<9> egress_port_1, bit<9> egress_port_2){
        bit<1> hash_value;
        hash(hash_value,
            HashAlgorithm.crc16,
            (bit<2>) 0,
            {standard_metadata.ingress_global_timestamp},
            (bit<2>) 2);

        if (hash_value == 0){
            /* TODO 4: Update the destination port */
            standard_metadata.egress_spec = egress_port_1;
        }
        else {
            /* TODO 4: Update the destination port */
            standard_metadata.egress_spec = egress_port_2;
        }
    }

    table repeater {
        key = {
            /* TODO 1: Match on the ingress port */
            standard_metadata.ingress_port: exact;
        }
        actions = {
            forward;
            random_forward;
            NoAction; /* NoAction results in the matched packets being dropped */
        }
        size = 3; /* TODO 2: Define the size of the table, i.e., the max number of entries */
        default_action = NoAction;
    }

    apply {
        /* TODO 5: Call the repeater table */
        repeater.apply();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

    /* Deparser not needed */

    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;

