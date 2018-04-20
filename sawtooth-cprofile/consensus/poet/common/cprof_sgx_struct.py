import os
import struct
from sawtooth_poet_common import sgx_structs
import cProfile

def create_random_buffer(length):
    return os.urandom(length)

def test_sgx_cpu_svn():
    sgx_cpu_svn = sgx_structs.SgxCpuSvn()
    # Verify sgx_cpu_svn unpacks properly    
    cpu_svn = create_random_buffer(sgx_structs.SgxCpuSvn.STRUCT_SIZE)

    sgx_cpu_svn.parse_from_bytes(cpu_svn) 
    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_cpu_svn = sgx_structs.SgxCpuSvn(svn=cpu_svn)

def test_sgx_attributes():
    sgx_attributes = sgx_structs.SgxAttributes()        
    # Verify sgx_attributes unpacks properly.
    flags = 0x0001020304050607
    xfrm = 0x08090a0b0c0d0e0f
    attributes = struct.pack(b'<QQ', flags, xfrm)
    sgx_attributes.parse_from_bytes(attributes)

    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_attributes = sgx_structs.SgxAttributes(flags=flags, xfrm=xfrm)


def test_sgx_measurement():
    sgx_measurement = sgx_structs.SgxMeasurement()

    # Verify sgx_measurement unpacks properly
    measurement = create_random_buffer(sgx_structs.SgxMeasurement.STRUCT_SIZE)
    sgx_measurement.parse_from_bytes(measurement)

    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_measurement = sgx_structs.SgxMeasurement(m=measurement)

def test_sgx_report_data():
    sgx_report_data = sgx_structs.SgxReportData()        

    # Verify sgx_report_data unpacks properly
    report_data = create_random_buffer(sgx_structs.SgxReportData.STRUCT_SIZE)
    sgx_report_data.parse_from_bytes(report_data)

    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_report_data = sgx_structs.SgxReportData(d=report_data)


def test_sgx_report_body():
    sgx_report_body = sgx_structs.SgxReportBody()        

    # Simply verify that buffer of correct size unpacks without error
    sgx_report_body.parse_from_bytes(create_random_buffer(sgx_structs.SgxReportBody.STRUCT_SIZE))

    # The report body is laid out as follows:
    #
    # sgx_cpu_svn_t           cpu_svn;        /* 0   */
    # sgx_misc_select_t       misc_select;    /* 16  */
    # uint8_t                 reserved1[28];  /* 20  */
    # sgx_attributes_t        attributes;     /* 48  */
    # sgx_measurement_t       mr_enclave;     /* 64  */
    # uint8_t                 reserved2[32];  /* 96  */
    # sgx_measurement_t       mr_signer;      /* 128 */
    # uint8_t                 reserved3[96];  /* 160 */
    # sgx_prod_id_t           isv_prod_id;    /* 256 */
    # sgx_isv_svn_t           isv_svn;        /* 258 */
    # uint8_t                 reserved4[60];  /* 260 */
    # sgx_report_data_t       report_data;    /* 320 */

    # sgx_cpu_svn = sgx_structs.SgxCpuSvn(cpu_svn=svn)
    # sgx_attributes = sgx_structs.SgxAttributes(flags=flags, xfrm=xfrm)
    # sgx_measurement_mr_enclave = sgx_structs.SgxMeasurement(m=mr_enclave)
    # sgx_measurement_mr_signer = sgx_structs.SgxMeasurement(m=mr_signer)
    # sgx_report_data = sgx_structs.SgxReportData(d=report_data)

    # Verify sgx_report_body unpacks properly
    svn = create_random_buffer(sgx_structs.SgxCpuSvn.STRUCT_SIZE)
    misc_select = 0x00010203
    reserved1 = b'\x00' * 28
    flags = 0x0405060708090a0b
    xfrm = 0x0c0d0e0f10111213
    mr_enclave = create_random_buffer(sgx_structs.SgxMeasurement.STRUCT_SIZE)
    reserved2 = b'\x00' * 32
    mr_signer = create_random_buffer(sgx_structs.SgxMeasurement.STRUCT_SIZE)
    reserved3 = b'\x00' * 96
    isv_prod_id = 0x1415
    isv_svn = 0x1617
    reserved4 = b'\x00' * 60
    report_data = create_random_buffer(sgx_structs.SgxReportData.STRUCT_SIZE)

    report_body = \
        struct.pack(
            '<{}sL{}sQQ{}s{}s{}s{}sHH{}s{}s'.format(
                len(svn),
                len(reserved1),
                len(mr_enclave),
                len(reserved2),
                len(mr_signer),
                len(reserved3),
                len(reserved4),
                len(report_data)
            ),
            svn,
            misc_select,
            reserved1,
            flags,
            xfrm,
            mr_enclave,
            reserved2,
            mr_signer,
            reserved3,
            isv_prod_id,
            isv_svn,
            reserved4,
            report_data)

    sgx_report_body.parse_from_bytes(report_body)

    

    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_cpu_svn = sgx_structs.SgxCpuSvn(svn=svn)
    sgx_attributes = sgx_structs.SgxAttributes(flags=flags, xfrm=xfrm)
    sgx_measurement_mr_enclave = sgx_structs.SgxMeasurement(m=mr_enclave)
    sgx_measurement_mr_signer = sgx_structs.SgxMeasurement(m=mr_signer)
    sgx_report_data = sgx_structs.SgxReportData(d=report_data)
    sgx_report_body = \
        sgx_structs.SgxReportBody(
            cpu_svn=sgx_cpu_svn,
            misc_select=misc_select,
            attributes=sgx_attributes,
            mr_enclave=sgx_measurement_mr_enclave,
            mr_signer=sgx_measurement_mr_signer,
            isv_prod_id=isv_prod_id,
            isv_svn=isv_svn,
            report_data=sgx_report_data)


def test_sgx_key_id():
    sgx_key_id = sgx_structs.SgxKeyId()

    # Verify sgx_key_id unpacks properly
    key_id = \
        create_random_buffer(
            sgx_structs.SgxKeyId.STRUCT_SIZE)
    sgx_key_id.parse_from_bytes(key_id)
    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_key_id = sgx_structs.SgxKeyId(identifier=key_id)

def test_sgx_report():
    sgx_report = sgx_structs.SgxReport()
    # Simply verify that buffer of correct size unpacks without error
    sgx_report.parse_from_bytes(
        create_random_buffer(
            sgx_structs.SgxReport.STRUCT_SIZE))

    # The report body is laid out as follows:
    #
    # sgx_report_body_t   body;   /* 0   */
    # sgx_key_id_t        key_id; /* 384 */
    # sgx_mac_t           mac;    /* 416 */

    # Verify sgx_report unpacks properly
    svn = \
        create_random_buffer(
            sgx_structs.SgxCpuSvn.STRUCT_SIZE)
    misc_select = 0x00010203
    reserved1 = b'\x00' * 28
    flags = 0x0405060708090a0b
    xfrm = 0x0c0d0e0f10111213
    mr_enclave = \
        create_random_buffer(
            sgx_structs.SgxMeasurement.STRUCT_SIZE)
    reserved2 = b'\x00' * 32
    mr_signer = \
        create_random_buffer(
            sgx_structs.SgxMeasurement.STRUCT_SIZE)
    reserved3 = b'\x00' * 96
    isv_prod_id = 0x1415
    isv_svn = 0x1617
    reserved4 = b'\x00' * 60
    report_data = \
        create_random_buffer(
            sgx_structs.SgxReportData.STRUCT_SIZE)
    report_body = \
        struct.pack(
            '<{}sL{}sQQ{}s{}s{}s{}sHH{}s{}s'.format(
                len(svn),
                len(reserved1),
                len(mr_enclave),
                len(reserved2),
                len(mr_signer),
                len(reserved3),
                len(reserved4),
                len(report_data)
            ),
            svn,
            misc_select,
            reserved1,
            flags,
            xfrm,
            mr_enclave,
            reserved2,
            mr_signer,
            reserved3,
            isv_prod_id,
            isv_svn,
            reserved4,
            report_data)
    key_id = \
        create_random_buffer(
            sgx_structs.SgxKeyId.STRUCT_SIZE)
    mac = create_random_buffer(16)
    report = \
        struct.pack(
            '<{}s{}s{}s'.format(
                len(report_body),
                len(key_id),
                len(mac)),
            report_body,
            key_id,
            mac)

    sgx_report.parse_from_bytes(report)


    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_cpu_svn = sgx_structs.SgxCpuSvn(svn=svn)
    sgx_attributes = sgx_structs.SgxAttributes(flags=flags, xfrm=xfrm)
    sgx_measurement_mr_enclave = sgx_structs.SgxMeasurement(m=mr_enclave)
    sgx_measurement_mr_signer = sgx_structs.SgxMeasurement(m=mr_signer)
    sgx_report_data = sgx_structs.SgxReportData(d=report_data)
    sgx_report_body = \
        sgx_structs.SgxReportBody(
            cpu_svn=sgx_cpu_svn,
            misc_select=misc_select,
            attributes=sgx_attributes,
            mr_enclave=sgx_measurement_mr_enclave,
            mr_signer=sgx_measurement_mr_signer,
            isv_prod_id=isv_prod_id,
            isv_svn=isv_svn,
            report_data=sgx_report_data)
    sgx_key_id = sgx_structs.SgxKeyId(identifier=key_id)
    sgx_report = \
        sgx_structs.SgxReport(
            body=sgx_report_body,
            key_id=sgx_key_id,
            mac=mac)

def test_sgx_basename():

    sgx_basename = sgx_structs.SgxBasename()
    # Verify sgx_basename unpacks properly
    basename = create_random_buffer(sgx_structs.SgxBasename.STRUCT_SIZE)
    sgx_basename.parse_from_bytes(basename)

    # Reset the object using the field values and verify that we
    # get expected serialized buffer
    sgx_basename = sgx_structs.SgxBasename(name=basename)

if __name__ == '__main__':
    print("\n====== cProfile: ./consensus/poet/common/cprofile_sgx_struct.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    test_sgx_cpu_svn()
    test_sgx_attributes()
    test_sgx_measurement()
    test_sgx_report_data()
    test_sgx_report_body()
    test_sgx_key_id()
    test_sgx_report()
    test_sgx_basename()

    pr.disable()
    pr.print_stats(sort='time')