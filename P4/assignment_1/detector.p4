/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

//My includes
#include "include/metadata.p4"
#include "include/headers.p4"
#include "include/parsers.p4"

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

    /* TODO: Define the register array(s) that you will use in the ingress pipeline */
    register<bit<32>>(3) ingress_regs_0;
    register<bit<32>>(3) ingress_regs_1;

    action forward(bit<9> egress_port){
        standard_metadata.egress_spec = egress_port;
    }

    table repeater {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            forward;
            NoAction;
        }
        size = 2;
        default_action = NoAction;
    }

    apply {
        /* TODO: This is where you need to increment the active counter */
        bit<32> iport = (bit<32>)(standard_metadata.ingress_port) - 1;
        bit<32> cnt_active = (bit<32>)(hdr.ipv4.ecn);
        repeater.apply();
        if (cnt_active == 0) {
            bit<32> cur_cnt;
            ingress_regs_0.read(cur_cnt, iport);
            ingress_regs_0.write(iport, cur_cnt + 1);
        } else {
            bit<32> cur_cnt;
            ingress_regs_1.read(cur_cnt, iport);
            ingress_regs_1.write(iport, cur_cnt + 1);
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    /* TODO: Define the register array(s) that you will use in the egress pipeline */
    register<bit<2>>(1) active_counter;
    register<bit<32>>(3) egress_regs_0;
    register<bit<32>>(3) egress_regs_1;

    apply {
        /* TODO: This is where you need to increment the active counter */
        /* TODO: You also need to indicate the active counter in every data packet using the IPv4 ecn field */
        bit<32> eport = (bit<32>)(standard_metadata.egress_port) - 1;
        bit<2> cnt_active;
        active_counter.read(cnt_active, 0);
        if (cnt_active == 0) {
            bit<32> cur_cnt;
            egress_regs_0.read(cur_cnt, eport);
            egress_regs_0.write(eport, cur_cnt + 1);
        } else {
            bit<32> cur_cnt;
            egress_regs_1.read(cur_cnt, eport);
            egress_regs_1.write(eport, cur_cnt + 1);
        }
        hdr.ipv4.ecn = cnt_active;
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply {

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