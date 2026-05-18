// Copyright (c) 2026 The Bitgesell developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <deploymentinfo.h>

#include <consensus/params.h>

#include <boost/test/unit_test.hpp>

#include <string>

BOOST_AUTO_TEST_SUITE(deploymentinfo_tests)

BOOST_AUTO_TEST_CASE(versionbits_deployment_names_are_complete)
{
    for (int i = 0; i < static_cast<int>(Consensus::MAX_VERSION_BITS_DEPLOYMENTS); ++i) {
        const auto deployment = static_cast<Consensus::DeploymentPos>(i);
        BOOST_REQUIRE(Consensus::ValidDeployment(deployment));

        const char* const name = VersionBitsDeploymentInfo[deployment].name;
        BOOST_REQUIRE_MESSAGE(name != nullptr, "missing deployment name at index " << i);
        BOOST_CHECK_MESSAGE(!std::string{name}.empty(), "empty deployment name at index " << i);
        BOOST_CHECK_EQUAL(DeploymentName(deployment), std::string{name});
    }
}

BOOST_AUTO_TEST_SUITE_END()
