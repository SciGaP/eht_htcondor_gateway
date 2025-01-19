"""
code to test function in htcondor.py
run in app folder: python -m tests.test_htcondor
"""

from blueprints import htcondor


def test_validate_explorer_staging():
    """input a dict"""
    # A sample input
    input = {
        "userName": "JunWang",
        "experimentName": "433",
        "dataCollection": "GRMHD_kharma-v3",
        "dataset": "Ma+0.94_w4",
        "imageList": "torus.out0.04406.h5\ntorus.out0.04262.h5\ntorus.out0.04967.h5\ntorus.out0.04741.h5\ntorus.out0.04389.h5\ntorus.out0.04707.h5\ntorus.out0.04788.h5\ntorus.out0.04292.h5\ntorus.out0.04586.h5\ntorus.out0.04843.h5\ntorus.out0.04723.h5\ntorus.out0.04667.h5\ntorus.out0.04322.h5\ntorus.out0.04901.h5\ntorus.out0.04094.h5\ntorus.out0.04645.h5\ntorus.out0.04666.h5\ntorus.out0.04971.h5",
        "parameters": {
            "rr_type": "multiple",
            "rr_value": "140,150,160",
            "tva_type": "range",
            "tva_value": "10:100:10",
            "rho_type": "single",
            "rho_value": "1.4705331615886175e+18",
        },
    }
    print(input)
    htcondor.validate_explorer_staging(input)

    return


def main():
    test_validate_explorer_staging()

    return


if __name__ == "__main__":
    main()
